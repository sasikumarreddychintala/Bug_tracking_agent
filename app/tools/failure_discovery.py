import os
import re
from typing import List, Dict, Any, Optional
from app.tools.sandbox import run_sandboxed_command

class DiscoveredFailure:
    def __init__(
        self,
        failure_id: str,
        test_name: str,
        test_file: str,
        error_type: str,
        error_message: str,
        crash_file: Optional[str] = None,
        crash_line: Optional[int] = None,
        raw_output: str = "",
        cluster_id: str = "CLUSTER-01",
        severity_score: int = 1,
        language: str = "python"
    ):
        self.failure_id = failure_id
        self.test_name = test_name
        self.test_file = test_file
        self.error_type = error_type
        self.error_message = error_message
        self.crash_file = crash_file
        self.crash_line = crash_line
        self.raw_output = raw_output
        self.cluster_id = cluster_id
        self.severity_score = severity_score
        self.language = language

    def to_dict(self) -> Dict[str, Any]:
        return {
            "failure_id": self.failure_id,
            "test_name": self.test_name,
            "test_file": self.test_file,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "crash_file": self.crash_file,
            "crash_line": self.crash_line,
            "cluster_id": self.cluster_id,
            "severity_score": self.severity_score,
            "language": self.language
        }

def discover_and_run_tests(repo_path: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Polyglot Failure Discovery Engine:
    Auto-detects tech stack (Python, JS/TS, Go, Rust, Java),
    executes tests in safe sandbox, captures failures, deduplicates, and ranks.
    """
    repo_path = os.path.abspath(repo_path)
    if not os.path.exists(repo_path):
        return {"status": "error", "error": f"Path not found: {repo_path}", "failures": [], "groups": []}

    # Detect test command based on stack
    test_cmd, language = _detect_test_command(repo_path)

    # Run test inside the target repository
    cmd_res = run_sandboxed_command(test_cmd, cwd=repo_path, timeout=timeout)
    stdout = cmd_res.get("stdout", "")
    stderr = cmd_res.get("stderr", "")
    combined_output = stdout + "\n" + stderr

    if language == "javascript/typescript":
        failures = _parse_jest_failures(combined_output, repo_path)
    elif language == "go":
        failures = _parse_go_failures(combined_output, repo_path)
    else:
        failures = _parse_pytest_failures(combined_output, repo_path)

    groups = _group_and_deduplicate_failures(failures)

    return {
        "status": "success",
        "detected_language": language,
        "test_command": test_cmd,
        "total_failures": len(failures),
        "unique_clusters_count": len(groups),
        "failures": [f.to_dict() for f in failures],
        "clusters": groups,
        "selected_primary_failure": failures[0].to_dict() if failures else None,
        "raw_test_output": combined_output[:2000]
    }

def _detect_test_command(repo_path: str) -> tuple[str, str]:
    files = []
    for root, dirs, fnames in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", ".venv", "dist", "build"}]
        files.extend([f.lower() for f in fnames])
        if len(files) > 100:
            break

    # 1. Check Python
    if any("pytest" in f or "test_" in f or "_test.py" in f for f in files) or "pyproject.toml" in files or "requirements.txt" in files:
        return "pytest -v --ignore=node_modules --ignore=frontend/node_modules", "python"

    # 2. Check JavaScript / TypeScript (npm / jest)
    if "package.json" in files:
        return "npm test", "javascript/typescript"

    # 3. Check Go
    if "go.mod" in files or any(f.endswith(".go") for f in files):
        return "go test ./...", "go"

    # 4. Check Rust
    if "cargo.toml" in files:
        return "cargo test", "rust"

    # Fallback to Python pytest
    return "pytest -v --ignore=node_modules", "python"

def _parse_pytest_failures(output: str, repo_path: str) -> List[DiscoveredFailure]:
    failures: List[DiscoveredFailure] = []
    lines = output.splitlines()
    current_test = None
    current_trace = []
    in_failure_block = False
    counter = 1

    for line in lines:
        if line.startswith("___") and line.endswith("___"):
            test_title = line.strip("_ ").strip()
            current_test = test_title
            current_trace = []
            in_failure_block = True
            continue
        
        if in_failure_block:
            current_trace.append(line)
            if line.startswith("===") or (line.startswith("FAILED ") and "::" in line):
                trace_text = "\n".join(current_trace)
                f_obj = _build_failure_object(f"FAIL-{counter:03d}", current_test or f"test_{counter}", trace_text, "python")
                failures.append(f_obj)
                counter += 1
                in_failure_block = False
                current_test = None
                current_trace = []

    if not failures:
        for line in lines:
            if line.startswith("FAILED ") and "::" in line:
                parts = line.split()[1].split("::")
                test_file = parts[0]
                test_name = parts[1] if len(parts) > 1 else "test"
                f_obj = DiscoveredFailure(
                    failure_id=f"FAIL-{counter:03d}",
                    test_name=test_name,
                    test_file=test_file,
                    error_type="AssertionOrRuntimeError",
                    error_message=f"Test {test_name} failed in {test_file}",
                    raw_output=output[:500],
                    language="python"
                )
                failures.append(f_obj)
                counter += 1

    return failures

def _parse_jest_failures(output: str, repo_path: str) -> List[DiscoveredFailure]:
    failures: List[DiscoveredFailure] = []
    counter = 1
    # Look for FAIL path/to/test.js
    for line in output.splitlines():
        if line.startswith("FAIL "):
            test_path = line.replace("FAIL ", "").strip()
            failures.append(DiscoveredFailure(
                failure_id=f"FAIL-JS-{counter:03d}",
                test_name=os.path.basename(test_path),
                test_file=test_path,
                error_type="JestTestFailure",
                error_message=f"Test suite failed in {test_path}",
                raw_output=output[:1000],
                language="javascript/typescript"
            ))
            counter += 1
    return failures

def _parse_go_failures(output: str, repo_path: str) -> List[DiscoveredFailure]:
    failures: List[DiscoveredFailure] = []
    counter = 1
    for line in output.splitlines():
        if "--- FAIL:" in line:
            parts = line.split()
            test_name = parts[2] if len(parts) > 2 else "TestFunc"
            failures.append(DiscoveredFailure(
                failure_id=f"FAIL-GO-{counter:03d}",
                test_name=test_name,
                test_file="main_test.go",
                error_type="GoTestFailure",
                error_message=line.strip(),
                raw_output=output[:1000],
                language="go"
            ))
            counter += 1
    return failures

def _build_failure_object(fid: str, test_name: str, trace_text: str, language: str) -> DiscoveredFailure:
    error_type = "Exception"
    error_msg = ""
    crash_file = None
    crash_line = None

    for line in reversed(trace_text.splitlines()):
        line_clean = line.strip()
        if ":" in line_clean and any(err in line_clean for err in ["Error", "Exception", "Fault", "AssertionError", "panic"]):
            parts = line_clean.split(":", 1)
            error_type = parts[0].strip()
            error_msg = parts[1].strip()
            break

    for line in reversed(trace_text.splitlines()):
        if "File " in line and ", line " in line:
            m = re.search(r'File ["\']([^"\']+)["\'], line (\d+)', line)
            if m:
                crash_file = m.group(1).replace("\\", "/")
                crash_line = int(m.group(2))
                break

    severity = 3 if "Error" in error_type and "Assertion" not in error_type else 2

    return DiscoveredFailure(
        failure_id=fid,
        test_name=test_name,
        test_file=crash_file or "tests/",
        error_type=error_type,
        error_message=error_msg,
        crash_file=crash_file,
        crash_line=crash_line,
        raw_output=trace_text,
        cluster_id=f"CLUSTER-{error_type}",
        severity_score=severity,
        language=language
    )

def _group_and_deduplicate_failures(failures: List[DiscoveredFailure]) -> List[Dict[str, Any]]:
    clusters: Dict[str, List[DiscoveredFailure]] = {}
    for f in failures:
        key = f"{f.error_type}@{f.crash_file}:{f.crash_line}"
        clusters.setdefault(key, []).append(f)

    result_clusters = []
    for idx, (sig, f_list) in enumerate(clusters.items(), start=1):
        result_clusters.append({
            "cluster_id": f"CLUSTER-{idx:02d}",
            "signature": sig,
            "failure_count": len(f_list),
            "primary_failure": f_list[0].to_dict(),
            "associated_tests": [f.test_name for f in f_list]
        })
    return result_clusters
