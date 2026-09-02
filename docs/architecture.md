# RepoTrace System Architecture

## Overview
RepoTrace is an autonomous agentic system for investigating software failures and determining their upstream root causes using repository evidence, competing hypotheses, sandboxed experiments, and independent verification.

```
                           USER
                            |
                            v
                         BUG CASE
                            |
                            v
                       CASE INTAKE
                            |
                            v
                    REPOSITORY MAPPER
                            |
                            v
                   INITIAL CODE EVIDENCE
                            |
                            v
                 BUG UNDERSTANDING AGENT
                            |
                            v
                CODE INVESTIGATION AGENT
                            |
                            v
                    HYPOTHESIS AGENT
                   (H1, H2, H3, ...)
                            |
                            v
                   EXPERIMENT SELECTOR
                            |
                            v
                  SAFE SANDBOX EXECUTION
                            |
                            v
                   VERIFICATION AGENT
                     +------+------+
                     |             |
                  WEAKENED     SUPPORTED
                     |             |
                     v             v
             INVESTIGATE MORE  ROOT CAUSE
                     |             |
                     +------<------+
                                   |
                                   v
                             REPORT AGENT
                                   |
                                   v
                              FINAL REPORT
                                   |
                                   v
                          SAVED TRAJECTORY
```

---

## 1. Agent Responsibilities

1. **Bug Understanding Agent** (`app/agents/bug_understanding.py`):
   - Ingests raw bug report, stack traces, and logs.
   - Outputs structured symptoms, confirmed facts, unknowns, entry points, and causal questions.
   - Does *not* decide final root cause or hallucinate unproven facts.

2. **Code Investigation Agent** (`app/agents/investigator.py`):
   - Uses deterministic repository tools (`read_file`, `search_code`, `find_symbol`, `parse_stacktrace`).
   - Traces execution from user input / entry points to the crash location.
   - Gathers concrete evidence items (`E1`, `E2`, `E3`).

3. **Hypothesis Generation Agent** (`app/agents/hypothesis.py`):
   - Formulates 2-4 competing root-cause hypotheses (`H1`, `H2`, `H3`).
   - Links supporting and contradicting evidence, notes missing proof, and proposes verification experiments.

4. **Independent Verification Agent** (`app/agents/verifier.py`):
   - Challenges each hypothesis against sandbox reproduction outputs and code evidence.
   - Distinguishes upstream root causes from downstream symptoms.
   - Assigns `SUPPORTED`, `WEAKENED`, `REJECTED`, or `UNCERTAIN` verdicts.

5. **Report Generation Agent** (`app/agents/report.py`):
   - Synthesizes executive diagnosis, root cause location, mechanism, evidence chain, reproduction status, rejected hypothesis rationales, fix recommendation, regression test recommendation, confidence, and limitations.

---

## 2. Deterministic Tool Layer
- **`list_files`**: Hierarchical directory traversal with `.git` and build cache exclusions.
- **`read_file`**: Line-numbered text reader with range bounds checking.
- **`search_code`**: Fast regex and literal keyword code search.
- **`find_symbol`**: AST-based Python class and function definition extractor.
- **`parse_stacktrace`**: Multi-frame traceback parser extracting exception type, message, file, line, and function.
- **`run_sandboxed_command`**: Security-hardened command executor enforcing a strict command allowlist (`pytest`, `ruff`, etc.) and timeout limits.

---

## 3. LangGraph Workflow State
State is managed via `InvestigationState` TypedDict containing:
- `run_id`, `case_id`, `repo_path`, `commit_sha`
- `symptoms`, `known_facts`, `unknowns`, `entry_points`, `investigation_questions`
- `repo_summary`, `file_tree`, `stacktrace_frames`, `evidence` list
- `hypotheses` list, `experiments` list, `verifications` list
- `report`, `trajectory` audit log, `investigation_round`, `is_finished`
