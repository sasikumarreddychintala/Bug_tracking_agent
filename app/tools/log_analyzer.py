from typing import Dict, Any, List

def analyze_logs(logs_content: str) -> Dict[str, Any]:
    if not logs_content:
        return {"errors": [], "warnings": [], "total_lines": 0}

    lines = logs_content.splitlines()
    errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    for idx, line in enumerate(lines, start=1):
        upper = line.upper()
        if any(w in upper for w in ["ERROR", "CRITICAL", "FATAL", "EXCEPTION"]):
            errors.append({"line": idx, "content": line.strip()})
        elif any(w in upper for w in ["WARN", "WARNING"]):
            warnings.append({"line": idx, "content": line.strip()})

    return {
        "total_lines": len(lines),
        "errors": errors,
        "warnings": warnings,
        "error_count": len(errors),
        "warning_count": len(warnings)
    }
