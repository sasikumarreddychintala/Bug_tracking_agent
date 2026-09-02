# 🚀 Running and Testing RepoTrace: A Practical Guide

Welcome to the **RepoTrace** developer and evaluation guide. This document explains how to set up your environment, run investigations across both operating modes, explore the web UI, and reproduce our benchmark evaluations.

---

## 🛠️ Step 1: Environment Setup

1. **Open PowerShell or Terminal** in the project root:
   ```bash
   cd C:\Downloads\OneDrive\Desktop\Bug_tracking_agent
   ```

2. **Create and Activate Virtual Environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
   *(If on Linux or macOS: `source .venv/bin/activate`)*

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🌐 Step 2: Launch the Interactive Web Dashboard

Launch the full Streamlit UI to visualize investigations in real time:

```bash
streamlit run app/streamlit_app.py
```

### What You Can Explore in the UI (`http://localhost:8501`):
- **Mode A (Known Failure)**: Choose any prebuilt fixture (`BUG-001` to `BUG-010`) or input your own custom repository path and stack trace.
- **Mode B (Discovery)**: Point RepoTrace to any repository path on your machine to automatically discover failing tests and investigate root causes.
- **Benchmarks Tab**: View the live 100% vs 60% accuracy scorecard and component ablation matrices.
- **6 Investigation Tabs**:
  - `🎯 Executive Diagnosis`: Verified upstream root cause, causal mechanism, fix, and regression test.
  - `🧩 Evidence Chain`: Line-numbered source code snippets pulled directly from disk.
  - `⚖️ Competing Hypotheses`: Decision breakdown for `H1`, `H2`, and `H3`.
  - `📜 Investigation Trace`: Chronological timeline of all 15+ tool events.
  - `🧪 Sandbox Execution`: Real-time `pytest` stdout and stderr logs.
  - `📥 Trace Export`: Downloadable Markdown (`.md`) audit trails and JSON logs.

---

## 🧪 Step 3: Run the Automated Test Suite

We have included a full suite of unit and integration tests verifying all agents, graph transitions, tools, and sandbox security:

```bash
# Run all 21 tests
python -m pytest tests/ -v

# Run linter
python -m ruff check app baseline evaluation tests
```

---

## 📊 Step 4: Reproduce the Benchmark & Ablation Study

Run our evaluation pipeline to reproduce our published scores:

```bash
# 1. Run Baseline V0 (Single-Shot LLM) across all 10 bug fixtures
python evaluation/run_baseline.py

# 2. Run RepoTrace across all 10 bug fixtures
python evaluation/run_repotrace.py

# 3. Compute 0-4 Root Cause Scores & Symptom-Trap Rates
python evaluation/evaluate.py

# 4. Run Component Ablation Experiments
python evaluation/run_ablations.py
```

---

## 💻 Step 5: Command Line Interface (CLI) Shortcuts

```bash
# Run quick demo on BUG-001
python -m app.main --demo

# Run on a specific bug fixture (BUG-001 to BUG-010)
python -m app.main --case BUG-002

# Run Autonomous Failure Discovery on any repository
python -m app.main --discover fixtures/bug001_quantity_zero
```
