import re
from typing import Dict, Any

def parse_stacktrace(trace: str) -> Dict[str, Any]:
    """
    Universal Polyglot Stack Trace Parser supporting:
    - Python (Traceback: File "...", line N)
    - JavaScript / TypeScript / Node.js (at Function (path/file.ts:line:col))
    - Java / Kotlin (at com.pkg.Class.method(File.java:line))
    - Go (goroutine N: path/file.go:line)
    - Rust (panicked at '...', file.rs:line:col)
    """
    if not trace or not trace.strip():
        return {
            "exception_type": "Unknown",
            "message": "No stack trace provided",
            "frames": [],
            "crash_frame": None,
            "language": "generic"
        }

    # 1. Try Python Traceback
    if "Traceback" in trace or 'File "' in trace:
        return _parse_python_trace(trace)

    # 2. Try JavaScript / TypeScript / Node.js
    if " at " in trace or "node_modules" in trace or "TypeError:" in trace or "ReferenceError:" in trace:
        return _parse_javascript_trace(trace)

    # 3. Try Go Panic / Test Failure
    if "panic:" in trace or "goroutine " in trace or ".go:" in trace:
        return _parse_go_trace(trace)

    # 4. Try Java / Kotlin
    if "Exception in thread" in trace or ("at " in trace and ".java:" in trace):
        return _parse_java_trace(trace)

    # 5. Try Rust Panic
    if "panicked at" in trace or ".rs:" in trace:
        return _parse_rust_trace(trace)

    # Generic Fallback Parser
    return _parse_generic_trace(trace)

def _parse_python_trace(trace: str) -> Dict[str, Any]:
    lines = trace.strip().splitlines()
    frames = []
    exception_type = "UnknownException"
    message = ""

    frame_pattern = re.compile(r'File ["\']([^"\']+)["\'], line (\d+)(?:, in (.+))?')

    for line in lines:
        match = frame_pattern.search(line)
        if match:
            fpath = match.group(1).replace("\\", "/")
            lineno = int(match.group(2))
            fn_name = match.group(3) if match.group(3) else "module"
            frames.append({
                "file": fpath,
                "line": lineno,
                "function": fn_name.strip()
            })

    # Last line is usually "ExceptionName: message"
    for line in reversed(lines):
        line_clean = line.strip()
        if ":" in line_clean and not line_clean.startswith("File "):
            parts = line_clean.split(":", 1)
            exception_type = parts[0].strip()
            message = parts[1].strip()
            break

    crash_frame = f"{frames[-1]['file']}:{frames[-1]['line']}" if frames else None

    return {
        "exception_type": exception_type,
        "message": message,
        "frames": frames,
        "crash_frame": crash_frame,
        "language": "python"
    }

def _parse_javascript_trace(trace: str) -> Dict[str, Any]:
    lines = trace.strip().splitlines()
    frames = []
    exception_type = "Error"
    message = ""

    # Check first line, e.g. "TypeError: Cannot read properties of undefined"
    first_line = lines[0].strip()
    if ":" in first_line:
        parts = first_line.split(":", 1)
        exception_type = parts[0].strip()
        message = parts[1].strip()

    # at FunctionName (path/file.js:12:34) or at path/file.js:12:34
    js_pattern = re.compile(r'at (?:([^\s(]+)\s+\()?([^:()]+):(\d+):(\d+)\)?')

    for line in lines:
        match = js_pattern.search(line)
        if match:
            fn_name = match.group(1) or "anonymous"
            fpath = match.group(2).replace("\\", "/").strip()
            lineno = int(match.group(3))
            frames.append({
                "file": fpath,
                "line": lineno,
                "function": fn_name
            })

    crash_frame = f"{frames[0]['file']}:{frames[0]['line']}" if frames else None

    return {
        "exception_type": exception_type,
        "message": message or first_line,
        "frames": frames,
        "crash_frame": crash_frame,
        "language": "javascript/typescript"
    }

def _parse_go_trace(trace: str) -> Dict[str, Any]:
    lines = trace.strip().splitlines()
    frames = []
    exception_type = "panic"
    message = ""

    go_pattern = re.compile(r'([^\s:]+\.go):(\d+)')
    for line in lines:
        if line.startswith("panic:"):
            message = line.replace("panic:", "").strip()
        match = go_pattern.search(line)
        if match:
            frames.append({
                "file": match.group(1).replace("\\", "/"),
                "line": int(match.group(2)),
                "function": "runtime"
            })

    crash_frame = f"{frames[0]['file']}:{frames[0]['line']}" if frames else None

    return {
        "exception_type": exception_type,
        "message": message or "Go runtime panic",
        "frames": frames,
        "crash_frame": crash_frame,
        "language": "go"
    }

def _parse_java_trace(trace: str) -> Dict[str, Any]:
    lines = trace.strip().splitlines()
    frames = []
    java_pattern = re.compile(r'at\s+([^\s(]+)\(([^:)]+):(\d+)\)')

    for line in lines:
        match = java_pattern.search(line)
        if match:
            frames.append({
                "file": match.group(2),
                "line": int(match.group(3)),
                "function": match.group(1)
            })

    return {
        "exception_type": "JavaException",
        "message": lines[0] if lines else "",
        "frames": frames,
        "crash_frame": f"{frames[0]['file']}:{frames[0]['line']}" if frames else None,
        "language": "java"
    }

def _parse_rust_trace(trace: str) -> Dict[str, Any]:
    lines = trace.strip().splitlines()
    frames = []
    rust_pattern = re.compile(r'([^\s:]+\.rs):(\d+)')

    for line in lines:
        match = rust_pattern.search(line)
        if match:
            frames.append({
                "file": match.group(1),
                "line": int(match.group(2)),
                "function": "panic"
            })

    return {
        "exception_type": "RustPanic",
        "message": trace.splitlines()[0] if trace else "",
        "frames": frames,
        "crash_frame": f"{frames[0]['file']}:{frames[0]['line']}" if frames else None,
        "language": "rust"
    }

def _parse_generic_trace(trace: str) -> Dict[str, Any]:
    # Extract any file:line pattern across all languages
    generic_pattern = re.compile(r'([a-zA-Z0-9_\-/\\]+\.[a-zA-Z0-9]+):(\d+)')
    frames = []
    for line in trace.splitlines():
        match = generic_pattern.search(line)
        if match:
            frames.append({
                "file": match.group(1).replace("\\", "/"),
                "line": int(match.group(2)),
                "function": "entry"
            })

    return {
        "exception_type": "GenericError",
        "message": trace.strip()[:150],
        "frames": frames,
        "crash_frame": f"{frames[0]['file']}:{frames[0]['line']}" if frames else None,
        "language": "generic"
    }
