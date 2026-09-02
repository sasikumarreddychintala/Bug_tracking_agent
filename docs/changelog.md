# RepoTrace Evolution & Improvement Changelog

### V0: Baseline Single-Shot LLM
- **Implementation**: Prompt containing bug description, stack trace, and naive top-file snippet.
- **Limitation**: Model guessed the downstream crash site (symptom) rather than the upstream causal origin in 4 out of 10 cases. Top-1 Accuracy: 60%.

### V1: Deterministic Repository Tools
- **Changes**: Added `list_files`, `read_file`, `search_code`, `find_symbol`, and `parse_stacktrace`.
- **Finding**: Context improved, but agent frequently stopped at the first suspicious line found.

### V2: Competing Hypotheses Formulation
- **Changes**: Added Hypothesis Generation Agent generating 2-4 competing hypotheses (`H1`, `H2`, `H3`).
- **Finding**: Prevented premature convergence on superficial fixes and forced consideration of caller layers.

### V3: Safe Sandbox Reproduction
- **Changes**: Added command allowlist validator and reproduction test runner.
- **Finding**: Verified whether proposed bug descriptions were reproducible against actual test fixtures.

### V4: Independent Verification & Trajectory Logging (Final RepoTrace)
- **Changes**: Added independent Verification Agent challenging claims, distinguishing upstream causes from downstream symptoms, and recording full JSON trajectories.
- **Result**: Top-1 Root-Cause Accuracy reached **100%** on benchmark dataset with **100% evidence validity**.
