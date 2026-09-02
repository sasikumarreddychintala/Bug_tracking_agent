# RepoTrace Reproduction Guide

This guide provides exact step-by-step instructions to reproduce the benchmarks on any clean machine.

## Prerequisites
- **Python**: 3.11, 3.12, or 3.13
- **Git**: Installed and available on PATH
- **OS**: Windows, macOS, or Linux

---

## 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/your-username/repotrace.git
cd repotrace

# Create virtual environment
python -m venv .venv

# Activate environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate environment (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 2. Running Demo Mode (BUG-001 Zero Quantity Bug)

```bash
# Run CLI demo
python -m app.main --demo
```

---

## 3. Running Automated Evaluation Benchmark

```bash
# Step 1: Run Baseline Benchmark across all 10 cases
python evaluation/run_baseline.py

# Step 2: Run RepoTrace Benchmark across all 10 cases
python evaluation/run_repotrace.py

# Step 3: Compute scoring rubric and generate results.csv
python evaluation/evaluate.py
```

Expected output:
- `evaluation/results/results.csv`
- `evaluation/results/results_summary.json`
- Baseline Accuracy: `60.0%`
- RepoTrace Accuracy: `100.0%`

---

## 4. Running the Interactive Streamlit UI

```bash
streamlit run app/streamlit_app.py
```

Open `http://localhost:8501` to view the live dashboard, evidence cards, competing hypotheses table, and trajectory viewer.

---

## 5. Running the Test Suite

```bash
python -m pytest tests/
```
