# ✅ RepoTrace: Step-by-Step Interactive Checklist

This document is your **interactive checklist** covering everything you need to test, run, and present RepoTrace for the **micro1 Agentic Workflows Hackathon 2026**.

---

## 📑 Checklist Overview
- [Phase 1: Setup & Environment](#phase-1-setup--environment)
- [Phase 2: Mode A (Investigate Known Failure)](#phase-2-mode-a-investigate-known-failure)
- [Phase 3: Mode B (Autonomous Failure Discovery)](#phase-3-mode-b-autonomous-failure-discovery)
- [Phase 4: Web UI & Trace Inspection](#phase-4-web-ui--trace-inspection)
- [Phase 5: Automated Tests & Linting](#phase-5-automated-tests--linting)
- [Phase 6: Benchmark & Ablation Replication](#phase-6-benchmark--ablation-replication)
- [Phase 7: Video Demonstration Guide](#phase-7-video-demonstration-guide)

---

## Phase 1: Setup & Environment

- [ ] **Python Version**: Python 3.11, 3.12, or 3.13 installed.
- [ ] **Virtual Environment**:
  ```bash
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

---

## Phase 2: Mode A (Investigate Known Failure)

- [ ] **Run Demo on BUG-001**:
  ```bash
  python -m app.main --demo
  ```
- [ ] **Verification Items**:
  - [x] Correctly identifies root cause in `src/cart.py:8-12` (not `pricing.py`).
  - [x] Formulates and tests competing hypotheses (`H1` Supported, `H2` Weakened).
  - [x] Validates line numbers and code snippets on disk.
  - [x] Saves audit trail to `trajectories/BUG-001/`.

---

## Phase 3: Mode B (Autonomous Failure Discovery)

- [ ] **Run Discovery on Any Repository**:
  ```bash
  python -m app.main --discover fixtures/bug001_quantity_zero
  ```
- [ ] **Verification Items**:
  - [x] Automatically detects test suite.
  - [x] Captures runtime test failures.
  - [x] Clusters similar failures by signature.
  - [x] Investigates primary failure and exports report.

---

## Phase 4: Web UI & Trace Inspection

- [ ] **Launch Streamlit Dashboard**:
  ```bash
  streamlit run app/streamlit_app.py
  ```
- [ ] **Verification Items**:
  - [x] **Sidebar**: Toggle between Mode A, Mode B, and Benchmarks.
  - [x] **Tab 1 (Executive Diagnosis)**: View verified root cause & fix.
  - [x] **Tab 2 (Evidence Chain)**: View line-numbered code snippets.
  - [x] **Tab 3 (Competing Hypotheses)**: View `SUPPORTED` vs `REJECTED` rationale.
  - [x] **Tab 4 (Investigation Trace)**: View chronological event timeline.
  - [x] **Tab 5 (Sandbox Execution)**: View raw test stdout/stderr.
  - [x] **Tab 6 (Trace Export)**: Download Markdown (`.md`) and JSON logs.

---

## Phase 5: Automated Tests & Linting

- [ ] **Run All 21 Tests**:
  ```bash
  python -m pytest tests/ -v
  ```
  *(Expected: 21 passed)*

- [ ] **Run Static Linter**:
  ```bash
  python -m ruff check app baseline evaluation tests
  ```
  *(Expected: All checks passed! 0 errors)*

---

## Phase 6: Benchmark & Ablation Replication

- [ ] **Run Benchmarks**:
  ```bash
  python evaluation/run_baseline.py
  python evaluation/run_repotrace.py
  python evaluation/evaluate.py
  python evaluation/run_ablations.py
  ```
- [ ] **Results Summary**:
  - **Baseline Top-1 Accuracy**: `60.0%` (Symptom trap rate: `40.0%`)
  - **RepoTrace Top-1 Accuracy**: `100.0%` (Symptom trap rate: `0.0%`)
  - **Ablations**: Confirms each agent adds measurable diagnostic power.

---

## Phase 7: Video Demonstration Guide (5 Minutes)

- [ ] **0:00 - 0:45 (The Problem)**: Explain the "Symptom Trap" and why standard AI fails on downstream crashes.
- [ ] **0:45 - 1:30 (Baseline Demo)**: Show Baseline V0 diagnosing `pricing.py` (the symptom).
- [ ] **1:30 - 3:00 (RepoTrace Live Investigation)**: Run RepoTrace, showing the 6 investigation tabs and the 31-event trace timeline.
- [ ] **3:00 - 4:00 (Benchmarks & Ablations)**: Show the 100% accuracy scorecard and ablation matrix.
- [ ] **4:00 - 5:00 (Trace Export & Closing)**: Download the Markdown report and wrap up with closing insights.
