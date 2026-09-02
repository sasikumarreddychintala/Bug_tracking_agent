import os
import re
import ast
from typing import Dict, Any, Optional

IGNORED_DIRS = {
    ".git", ".venv", "venv", "env", "__pycache__",
    ".pytest_cache", ".ruff_cache", "node_modules",
    "dist", "build", ".next", ".nuxt", "coverage", ".idea", ".vscode"
}

def search_code(root: str, query: str, file_filter: Optional[str] = None, is_regex: bool = False) -> Dict[str, Any]:
    root = os.path.abspath(root)
    matches = []
    if not os.path.exists(root):
        return {"status": "error", "error": f"Path not found: {root}", "matches": []}

    try:
        pattern = re.compile(query, re.IGNORECASE) if is_regex else None
    except re.error as e:
        return {"status": "error", "error": f"Invalid regex: {e}", "matches": []}

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        for f in filenames:
            if file_filter and not f.endswith(file_filter):
                continue
            full_path = os.path.join(dirpath, f)
            rel_path = os.path.relpath(full_path, root).replace(os.sep, "/")
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as file_obj:
                    for line_num, line in enumerate(file_obj, start=1):
                        matched = False
                        if pattern:
                            if pattern.search(line):
                                matched = True
                        else:
                            if query.lower() in line.lower():
                                matched = True
                        if matched:
                            matches.append({
                                "path": rel_path,
                                "line": line_num,
                                "snippet": line.strip()
                            })
                            if len(matches) >= 50:
                                return {
                                    "status": "success",
                                    "query": query,
                                    "total_matches": len(matches),
                                    "matches": matches
                                }
            except Exception:
                continue

    return {
        "status": "success",
        "query": query,
        "total_matches": len(matches),
        "matches": matches
    }

def find_symbol(root: str, symbol_name: str) -> Dict[str, Any]:
    root = os.path.abspath(root)
    definitions = []
    if not os.path.exists(root):
        return {"status": "error", "error": f"Path not found: {root}", "definitions": []}

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        for f in filenames:
            if not f.endswith(".py"):
                continue
            full_path = os.path.join(dirpath, f)
            rel_path = os.path.relpath(full_path, root).replace(os.sep, "/")
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as file_obj:
                    content = file_obj.read()
                tree = ast.parse(content, filename=full_path)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name == symbol_name:
                        definitions.append({
                            "type": "function",
                            "symbol": node.name,
                            "path": rel_path,
                            "line": node.lineno,
                            "docstring": ast.get_docstring(node) or ""
                        })
                    elif isinstance(node, ast.ClassDef) and node.name == symbol_name:
                        definitions.append({
                            "type": "class",
                            "symbol": node.name,
                            "path": rel_path,
                            "line": node.lineno,
                            "docstring": ast.get_docstring(node) or ""
                        })
            except Exception:
                continue

    return {
        "status": "success",
        "symbol": symbol_name,
        "total_definitions": len(definitions),
        "definitions": definitions
    }
