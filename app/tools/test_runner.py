import os
from typing import Dict, Any
from app.tools.sandbox import run_sandboxed_command

def run_reproduction_test(repo_path: str, command: str, timeout: int = 30) -> Dict[str, Any]:
    repo_path = os.path.abspath(repo_path)
    if not os.path.exists(repo_path):
        return {
            "status": "error",
            "error": f"Repository path does not exist: {repo_path}",
            "reproduced": False
        }

    # If command targets a non-existent 'tests/' directory, adapt to discovered tests or root pytest
    if command.startswith("pytest tests/") and not os.path.exists(os.path.join(repo_path, "tests")):
        # Check for alternative test directories (e.g. server/tests, test/, src/tests)
        for cand in ["server/tests", "server/test", "src/tests", "test", "tests"]:
            if os.path.exists(os.path.join(repo_path, cand)):
                command = f"pytest {cand}"
                break
        else:
            command = "pytest"

    result = run_sandboxed_command(command, cwd=repo_path, timeout=timeout)
    out = (result.get("stdout", "") + " " + result.get("stderr", ""))
    reproduced = (result.get("exit_code") != 0) and any(bw in out for bw in ["FAIL", "ERROR", "Error", "Exception", "Traceback", "AssertionError"])
    result["reproduced"] = reproduced
    return result
