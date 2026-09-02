import os
from typing import Dict, Any
from app.tools.filesystem import list_files

def map_repository(repo_path: str) -> Dict[str, Any]:
    repo_path = os.path.abspath(repo_path)
    if not os.path.exists(repo_path):
        return {"status": "error", "error": f"Repository not found: {repo_path}"}

    files = list_files(repo_path, max_depth=4)
    file_paths = [f["path"].lower() for f in files]

    # Detect Languages & Frameworks
    detected_languages = []
    has_python = any(p.endswith(".py") for p in file_paths) or "requirements.txt" in file_paths or "pyproject.toml" in file_paths
    has_js = any(p.endswith((".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs")) for p in file_paths) or "package.json" in file_paths
    has_go = any(p.endswith(".go") for p in file_paths) or "go.mod" in file_paths
    has_rust = any(p.endswith(".rs") for p in file_paths) or "cargo.toml" in file_paths
    has_java = any(p.endswith((".java", ".kt", ".gradle")) for p in file_paths) or "pom.xml" in file_paths

    if has_python:
        detected_languages.append("Python")
    if has_js:
        detected_languages.append("JavaScript/TypeScript")
    if has_go:
        detected_languages.append("Go")
    if has_rust:
        detected_languages.append("Rust")
    if has_java:
        detected_languages.append("Java")

    primary_language = "/".join(detected_languages) if detected_languages else "Generic"

    # Detect Test Suites
    test_frameworks = []
    if any("pytest" in p or "test_" in p or "_test.py" in p for p in file_paths):
        test_frameworks.append("pytest")
    if any("jest" in p or ".test.js" in p or ".spec.ts" in p for p in file_paths) or "package.json" in file_paths:
        test_frameworks.append("npm/jest")
    if has_go:
        test_frameworks.append("go test")
    if has_rust:
        test_frameworks.append("cargo test")

    return {
        "status": "success",
        "repo_path": repo_path,
        "total_files": len(files),
        "file_tree": [f["path"] for f in files],
        "language": primary_language,
        "detected_languages": detected_languages,
        "test_frameworks": test_frameworks,
        "has_pytest": "pytest" in test_frameworks,
        "has_package_json": "package.json" in file_paths,
        "has_pyproject": "pyproject.toml" in file_paths,
        "has_requirements": "requirements.txt" in file_paths,
        "has_readme": any("readme" in p for p in file_paths)
    }
