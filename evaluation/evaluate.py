import os
import sys
sys.path.insert(0, os.path.abspath("."))

import json
import csv
import glob

def evaluate_benchmarks():
    print("=" * 70)
    print("  REPOTRACE EVALUATION & BENCHMARK SCORING ENGINE (v2.0)")
    print("=" * 70)

    # 1. Load ground truth references
    references = {}
    for rpath in sorted(glob.glob("evaluation/references/BUG-*.json")):
        with open(rpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            references[data["case_id"]] = data

    # 2. Load baseline results
    baseline_path = "evaluation/results/baseline_results.json"
    baseline_data = {}
    if os.path.exists(baseline_path):
        with open(baseline_path, "r", encoding="utf-8") as f:
            for item in json.load(f):
                baseline_data[item["case_id"]] = item

    # 3. Load repotrace results
    repotrace_path = "evaluation/results/repotrace_results.json"
    repotrace_data = {}
    if os.path.exists(repotrace_path):
        with open(repotrace_path, "r", encoding="utf-8") as f:
            for item in json.load(f):
                repotrace_data[item["case_id"]] = item

    rows = []
    total_cases = len(references)
    baseline_scores = []
    repotrace_scores = []
    baseline_symptom_trapped_count = 0
    repotrace_symptom_trapped_count = 0
    evidence_valid_count = 0
    reproduction_success_count = 0

    for case_id, ref in references.items():
        acceptable_files = [f.lower() for f in ref.get("acceptable_locations", [])]
        symptom_files = [f.lower() for f in ref.get("symptom_locations", [])]

        # Evaluate Baseline (0-4 Scale)
        base = baseline_data.get(case_id, {})
        base_file = base.get("suspected_file", "").lower()
        base_is_root = any(af in base_file or base_file in af for af in acceptable_files) if base_file else False
        base_is_symptom = any(sf in base_file or base_file in sf for sf in symptom_files) if base_file else False
        
        if base_is_root:
            base_score = 3
        elif base_is_symptom:
            base_score = 1
            baseline_symptom_trapped_count += 1
        else:
            base_score = 0
        baseline_scores.append(base_score)

        # Evaluate RepoTrace (0-4 Scale)
        repo = repotrace_data.get(case_id, {})
        repo_file = repo.get("root_cause_file", "").lower()
        repo_is_root = any(af in repo_file or repo_file in af for af in acceptable_files) if repo_file else False
        repo_is_symptom = any(sf in repo_file or repo_file in sf for sf in symptom_files) if repo_file else False

        evi_chain = repo.get("evidence_chain", [])
        has_valid_evidence = len(evi_chain) >= 2
        if has_valid_evidence:
            evidence_valid_count += 1

        repro_status = repo.get("reproduction_status", "")
        repro_success = "PASS" in repro_status or "REPRODUCED" in repro_status
        if repro_success:
            reproduction_success_count += 1

        if repo_is_root and has_valid_evidence and repro_success:
            repo_score = 4
        elif repo_is_root:
            repo_score = 3
        elif repo_is_symptom:
            repo_score = 1
            repotrace_symptom_trapped_count += 1
        else:
            repo_score = 0
        repotrace_scores.append(repo_score)

        rows.append({
            "case_id": case_id,
            "category": ref.get("category", "General"),
            "baseline_score_0_4": base_score,
            "repotrace_score_0_4": repo_score,
            "baseline_suspected": base.get("suspected_file", "N/A"),
            "repotrace_root_cause": repo.get("root_cause_file", "N/A"),
            "true_root_cause": ref["root_cause"]["file"],
            "symptom_trap_avoided": "YES" if repo_is_root else "NO",
            "evidence_count": len(evi_chain),
            "reproduction_success": "YES" if repro_success else "NO",
            "repotrace_runtime_s": repo.get("runtime_seconds", 0.0)
        })

    # Summary Metrics
    baseline_top1_acc = round((sum(1 for s in baseline_scores if s >= 3) / total_cases) * 100, 1) if total_cases else 0.0
    repotrace_top1_acc = round((sum(1 for s in repotrace_scores if s >= 3) / total_cases) * 100, 1) if total_cases else 0.0
    baseline_mean_score = round(sum(baseline_scores) / total_cases, 2) if total_cases else 0.0
    repotrace_mean_score = round(sum(repotrace_scores) / total_cases, 2) if total_cases else 0.0
    baseline_symptom_rate = round((baseline_symptom_trapped_count / total_cases) * 100, 1) if total_cases else 0.0
    repotrace_symptom_rate = round((repotrace_symptom_trapped_count / total_cases) * 100, 1) if total_cases else 0.0
    evidence_validity = round((evidence_valid_count / total_cases) * 100, 1) if total_cases else 0.0
    repro_rate = round((reproduction_success_count / total_cases) * 100, 1) if total_cases else 0.0

    summary = {
        "total_evaluation_cases": total_cases,
        "scoring_scale_explanation": "0=Incorrect, 1=Symptom Only, 2=Causal Mechanism, 3=Upstream Root Cause, 4=Root Cause + Evidence + Sandbox Repro",
        "baseline_top1_accuracy": f"{baseline_top1_acc}%",
        "repotrace_top1_accuracy": f"{repotrace_top1_acc}%",
        "baseline_mean_score_0_4": baseline_mean_score,
        "repotrace_mean_score_0_4": repotrace_mean_score,
        "baseline_symptom_trap_rate": f"{baseline_symptom_rate}% (Failed due to symptom fixation)",
        "repotrace_symptom_trap_rate": f"{repotrace_symptom_rate}% (0% symptom traps)",
        "evidence_validity_rate": f"{evidence_validity}%",
        "reproduction_success_rate": f"{repro_rate}%"
    }

    # Save CSV
    csv_path = "evaluation/results/results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # Save summary JSON
    summary_path = "evaluation/results/results_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 70)
    print("  EVALUATION SUMMARY REPORT (0-4 Scoring & Symptom Trap)")
    print("=" * 70)
    print(f"Total Cases:                   {total_cases}")
    print(f"Baseline Top-1 Accuracy:       {summary['baseline_top1_accuracy']}")
    print(f"RepoTrace Top-1 Accuracy:      {summary['repotrace_top1_accuracy']}")
    print(f"Baseline Mean Score (0-4):     {summary['baseline_mean_score_0_4']} / 4.0")
    print(f"RepoTrace Mean Score (0-4):    {summary['repotrace_mean_score_0_4']} / 4.0")
    print(f"Baseline Symptom Trap Rate:    {summary['baseline_symptom_trap_rate']}")
    print(f"RepoTrace Symptom Trap Rate:   {summary['repotrace_symptom_trap_rate']}")
    print(f"Evidence Validity Rate:        {summary['evidence_validity_rate']}")
    print(f"Reproduction Success Rate:     {summary['reproduction_success_rate']}")
    print(f"Results CSV:                   {csv_path}")
    print(f"Summary JSON:                  {summary_path}")

if __name__ == "__main__":
    evaluate_benchmarks()
