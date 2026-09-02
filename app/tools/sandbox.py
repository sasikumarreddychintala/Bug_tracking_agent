import time
import subprocess
import os
from typing import Dict, Any

ALLOWED_COMMAND_PREFIXES = [
    # Python
    "pytest",
    "python -m pytest",
    "python -m unittest",
    "python -m doctest",
    "ruff check",
    "python tests/",
    "python -c",
    # JavaScript / TypeScript / Node
    "npm test",
    "npm run test",
    "npx jest",
    "npx vitest",
    "npx mocha",
    "yarn test",
    "pnpm test",
    "node --test",
    # Go
    "go test",
    # Rust
    "cargo test",
    # Java
    "mvn test",
    "gradle test",
    "./gradlew test",
    # C/C++
    "ctest",
    "make test"
]

DISALLOWED_TOKENS = [
    "rm ", "del ", "rmdir", "rmtree",
    "curl ", "wget ", "nc ", "bash ", "sh ",
    "sudo ", "chmod ", "chown ", "dd ",
    "> ", ">> ", ":()", "format "
]

def validate_command(command: str) -> Dict[str, Any]:
    cmd_clean = command.strip()
    
    for token in DISALLOWED_TOKENS:
        if token in cmd_clean.lower():
            return {
                "allowed": False,
                "reason": f"Command contains disallowed dangerous token: '{token.strip()}'"
            }

    is_allowed = any(cmd_clean.startswith(prefix) for prefix in ALLOWED_COMMAND_PREFIXES)
    if not is_allowed:
        return {
            "allowed": False,
            "reason": f"Command '{cmd_clean}' is not in the approved multi-stack test allowlist (pytest, npm test, jest, go test, cargo test, etc.)"
        }

    return {"allowed": True, "command": cmd_clean}

def run_sandboxed_command(command: str, cwd: str, timeout: int = 30) -> Dict[str, Any]:
    validation = validate_command(command)
    if not validation["allowed"]:
        return {
            "status": "rejected",
            "command": command,
            "stdout": "",
            "stderr": validation["reason"],
            "exit_code": -1,
            "passed": False,
            "duration_ms": 0
        }

    start_time = time.time()
    try:
        sub_env = os.environ.copy()
        src_dir = os.path.join(cwd, "src")
        extra_paths = [cwd, src_dir] if os.path.exists(src_dir) else [cwd]
        sub_env["PYTHONPATH"] = os.pathsep.join(extra_paths + [sub_env.get("PYTHONPATH", "")])

        res = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=sub_env
        )
        duration_ms = int((time.time() - start_time) * 1000)
        return {
            "status": "success",
            "command": command,
            "stdout": res.stdout,
            "stderr": res.stderr,
            "exit_code": res.returncode,
            "passed": res.returncode == 0,
            "duration_ms": duration_ms
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "command": command,
            "stdout": "",
            "stderr": f"Command timed out after {timeout} seconds",
            "exit_code": -1,
            "passed": False,
            "duration_ms": timeout * 1000
        }
    except Exception as e:
        return {
            "status": "error",
            "command": command,
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1,
            "passed": False,
            "duration_ms": 0
        }
