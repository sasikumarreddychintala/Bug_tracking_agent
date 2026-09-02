# 🔍 RepoTrace: Autonomous Bug Root-Cause Investigation System

> **micro1 Agentic Workflows Hackathon 2026 / Frontier Engineering Challenge**  
> *"Trace the cause, not just the error."*

---

## 💡 Why We Built RepoTrace
If you have ever pasted a Python traceback or error log into ChatGPT or GitHub Copilot, you have probably noticed a major limitation: **they almost always try to fix the exact line where the program crashed.**

In software engineering, this is known as the **"Symptom Trap."**

### The Problem in Action:
Imagine an e-commerce backend where adding a promo item with quantity `0` crashes during checkout in `pricing.py:4` with a `ZeroDivisionError`:
- **What a standard AI does**: It adds `if quantity == 0: return 0` right inside `pricing.py`. **This is dangerous**—it masks the crash and allows users to check out invalid $0 orders!
- **What an experienced engineer does**: Traces callers backwards to find where the `0` came from (`cart.py`). The true defect is that `cart.py` failed to validate cart items before checkout.

We built **RepoTrace** to debug like a senior engineer—by exploring the repository, gathering line-numbered code evidence, testing competing theories in an isolated sandbox, and identifying the **true upstream root cause**.

---

## 🧠 How RepoTrace Investigates (7-Stage Workflow)

Instead of relying on single-shot LLM guesses, RepoTrace runs an autonomous forensic investigation:

```
  1. MAP REPO           ➔ Scans directory structure & detects tech stacks (Python, JS, Go, Rust, Java)
  2. PARSE CRASH        ➔ Deconstructs stack trace into exact file coordinates & exception types
  3. GATHER EVIDENCE    ➔ Reads source files on disk & traces caller-callee paths
  4. FORM HYPOTHESES    ➔ Creates competing theories (H1: Upstream root cause vs H2: Downstream symptom)
  5. RUN EXPERIMENTS    ➔ Executes tests in a secure sandbox to confirm runtime behavior
  6. VALIDATE EVIDENCE  ➔ Verifies all cited line numbers on disk to eliminate hallucinations
  7. VERIFY & REPORT    ➔ Selects winning root cause, suggests a concrete fix, & exports an audit trace
```

---

## ⚡ Two Operating Modes

### 1. Mode A: Investigate Known Failure (Interactive)
- **Input**: Repository + Bug Description + Stack Trace / Error Log.
- **Workflow**: Reads your logs, traces the call graph, tests rival hypotheses, and proves the upstream root cause.

### 2. Mode B: Discover Test Failures (Autonomous Engine)
- **Input**: Repository path only.
- **Workflow**: Scans the codebase, detects test frameworks, executes the test suite in our sandbox, deduplicates failures into clusters, and investigates the primary defect with zero manual intervention.

---

## 📜 First-Class Observable Traces
We believe developers shouldn't have to blindly trust an AI's output. RepoTrace treats traces as a **core engineering audit log**:
- Emits structured `TraceEvent` records across all 7 investigation stages.
- Stores zero private or hidden chain-of-thought.
- Exports dual-format audit trails in **human-readable Markdown (`.md`)** and **structured JSON (`.json`)**.

---

## 📊 Scientific Benchmark Evaluation & Ablation Results

We tested RepoTrace across **10 real-world benchmark bug cases** against isolated ground-truth references:

### 1. Overall Performance Comparison
| Metric | Baseline V0 (Single-Shot LLM) | RepoTrace (Agentic Workflow) | Improvement |
| :--- | :---: | :---: | :---: |
| **Top-1 Root-Cause Accuracy** | **60.0%** (6/10) | **100.0%** (10/10) | **+40.0% Boost** |
| **Mean Score (0 to 4 Scale)** | **2.2 / 4.0** | **4.0 / 4.0** | **+1.8 Points** |
| **Symptom-Trap Rate** | **40.0%** (Failed at crash line) | **0.0%** | **40% Reduction** |
| **Evidence Validity Rate** | 0.0% (Ungrounded) | **100.0%** (Verified on disk) | **100% Validated** |
| **Reproduction Success Rate** | 0.0% | **100.0%** | **100% Verified** |

### 2. Component Ablation Study Matrix
| System Configuration | Hypotheses Agent | Code Search Tool | Sandbox Repro | Verification Agent | Accuracy | Symptom Trap Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline V0 (Single-Shot LLM)** | ❌ NO | ❌ NO | ❌ NO | ❌ NO | **60.0%** | 40.0% |
| **RepoTrace (No Code Search)** | ✅ YES | ❌ NO | ✅ YES | ✅ YES | **70.0%** | 30.0% |
| **RepoTrace (No Hypotheses Agent)** | ❌ NO | ✅ YES | ✅ YES | ✅ YES | **80.0%** | 20.0% |
| **RepoTrace (No Verification Agent)**| ✅ YES | ✅ YES | ✅ YES | ❌ NO | **70.0%** | 30.0% |
| **Full RepoTrace (All Components)** | ✅ YES | ✅ YES | ✅ YES | ✅ YES | **100.0%** | **0.0%** |

---

## 🚀 Quickstart Guide

### 1. Setup Environment
```bash
git clone https://github.com/your-username/repotrace.git
cd repotrace
python -m venv .venv
.venv\Scripts\Activate.ps1   # On Windows (or source .venv/bin/activate on Linux/Mac)
pip install -r requirements.txt
```

### 2. Launch Interactive Streamlit Web UI
```bash
streamlit run app/streamlit_app.py
```

### 3. Run CLI Demo (Mode A)
```bash
python -m app.main --demo
```

### 4. Run Autonomous Failure Discovery (Mode B)
```bash
python -m app.main --discover fixtures/bug001_quantity_zero
```

### 5. Run Benchmark Suite & Ablations
```bash
python evaluation/run_baseline.py
python evaluation/run_repotrace.py
python evaluation/evaluate.py
python evaluation/run_ablations.py
```

### 6. Run Unit & Integration Tests (21 Tests)
```bash
python -m pytest tests/ -v
```

---

## 🌐 Polyglot & Multi-Stack Ready
- **Supported Languages**: Python (`pytest`), JavaScript/TypeScript (`Jest`, `Vitest`), Go (`go test`), Rust (`cargo test`), Java (`Maven/Gradle`).
- **High Speed**: Built-in smart directory filtering automatically skips heavy folders like `node_modules` and `.venv`, running full investigations in **under 10 seconds**.
