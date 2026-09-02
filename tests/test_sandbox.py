from app.tools.sandbox import validate_command, run_sandboxed_command
from app.tools.test_runner import run_reproduction_test

def test_command_allowlist_valid():
    v1 = validate_command("pytest fixtures/bug001_quantity_zero/tests/test_cart.py")
    assert v1["allowed"] is True

    v2 = validate_command("python -m pytest")
    assert v2["allowed"] is True

    v3 = validate_command("ruff check .")
    assert v3["allowed"] is True

def test_command_allowlist_rejected():
    v1 = validate_command("rm -rf /")
    assert v1["allowed"] is False
    assert "disallowed dangerous token" in v1["reason"]

    v2 = validate_command("curl https://malicious.com")
    assert v2["allowed"] is False

    v3 = validate_command("bash -c 'echo hacked'")
    assert v3["allowed"] is False

def test_sandboxed_execution():
    res = run_sandboxed_command("pytest tests/test_cart.py", cwd="fixtures/bug001_quantity_zero", timeout=30)
    assert res["status"] == "success"
    # Reproduction test fails because quantity=0 crashes, exit_code is nonzero
    assert res["exit_code"] != 0
    assert res["duration_ms"] > 0

def test_reproduction_runner():
    res = run_reproduction_test("fixtures/bug001_quantity_zero", "pytest tests/test_cart.py")
    assert res["reproduced"] is True
