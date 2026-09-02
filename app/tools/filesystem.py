import os
from typing import List, Dict, Any, Optional

IGNORED_DIRS = {
    ".git", ".venv", "venv", "env", "__pycache__",
    ".pytest_cache", ".ruff_cache", "node_modules",
    "dist", "build", ".next", ".nuxt", "coverage", ".idea", ".vscode"
}

def list_files(root: str, max_depth: int = 4, filter_ext: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    results = []
    root = os.path.abspath(root)
    if not os.path.exists(root):
        return results

    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        depth = 0 if rel_dir == "." else rel_dir.count(os.sep) + 1
        if depth > max_depth:
            dirnames.clear()
            continue

        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]

        for f in filenames:
            ext = os.path.splitext(f)[1].lower()
            if filter_ext and ext not in filter_ext:
                continue
            full_path = os.path.join(dirpath, f)
            rel_path = os.path.relpath(full_path, root).replace(os.sep, "/")
            try:
                size = os.path.getsize(full_path)
            except OSError:
                size = 0
            results.append({
                "path": rel_path,
                "size": size,
                "type": "file"
            })
            if len(results) >= 500:
                break
    return results

def read_file(file_path: str, start_line: int = 1, end_line: Optional[int] = None) -> Dict[str, Any]:
    if not os.path.exists(file_path):
        return {
            "status": "error",
            "error": f"File not found: {file_path}",
            "content": ""
        }

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        total = len(lines)
        end = end_line if end_line is not None else total
        start_idx = max(0, start_line - 1)
        end_idx = min(total, end)

        selected_lines = lines[start_idx:end_idx]
        numbered_content = "".join([f"{i + start_line:4d} | {line}" for i, line in enumerate(selected_lines)])

        return {
            "status": "success",
            "file_path": file_path,
            "total_lines": total,
            "start_line": start_line,
            "end_line": end_idx,
            "content": numbered_content,
            "raw_content": "".join(selected_lines)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "content": ""
        }
