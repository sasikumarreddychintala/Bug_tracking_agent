import os
from typing import List, Dict, Any
from app.schemas.evidence import Evidence, EvidenceType
from app.schemas.case import BugCase
from app.tools.filesystem import read_file
from app.tools.search import search_code
from app.tools.stacktrace import parse_stacktrace

def run_code_investigation(
    case: BugCase,
    entry_points: List[str],
    stacktrace_frames: List[Dict[str, Any]],
    repo_path: str
) -> Dict[str, Any]:
    evidence_list: List[Evidence] = []
    observations: List[str] = []
    evidence_counter = 1

    # 1. Parse stacktrace if present and record frame evidence
    if case.stack_trace:
        st_data = parse_stacktrace(case.stack_trace)
        frames = st_data.get("frames", [])
        if frames:
            observations.append(f"Stack trace analysis identified {len(frames)} frames. Top crash frame: {frames[-1].get('file')}:{frames[-1].get('line')}")
            evidence_list.append(Evidence(
                id=f"E{evidence_counter}",
                type=EvidenceType.STACKTRACE,
                path=frames[-1].get("file") if frames else None,
                line_start=frames[-1].get("line") if frames else None,
                line_end=frames[-1].get("line") if frames else None,
                content_or_summary=f"Crash: {st_data.get('exception_type')}: {st_data.get('message')} at {frames[-1].get('file')}:{frames[-1].get('line')}",
                source_tool="parse_stacktrace"
            ))
            evidence_counter += 1

    # 2. Inspect files mentioned in stack trace and entry points
    inspected_paths = set()
    for frame in stacktrace_frames:
        fpath = frame.get("file")
        if fpath and fpath not in inspected_paths:
            full = os.path.join(repo_path, fpath)
            if os.path.exists(full):
                inspected_paths.add(fpath)
                line_no = frame.get("line", 1)
                start_l = max(1, line_no - 15)
                end_l = line_no + 15
                f_res = read_file(full, start_line=start_l, end_line=end_l)
                if f_res.get("status") == "success":
                    evidence_list.append(Evidence(
                        id=f"E{evidence_counter}",
                        type=EvidenceType.FILE,
                        path=fpath,
                        line_start=start_l,
                        line_end=end_l,
                        content_or_summary=f_res.get("content", ""),
                        source_tool="read_file"
                    ))
                    observations.append(f"Read {fpath} around line {line_no} where execution failed or branched.")
                    evidence_counter += 1

    # 3. Inspect entry points
    for ep in entry_points:
        clean_ep = ep.split(":")[0]
        if clean_ep and clean_ep not in inspected_paths:
            full = os.path.join(repo_path, clean_ep)
            if os.path.exists(full) and os.path.isfile(full):
                inspected_paths.add(clean_ep)
                f_res = read_file(full, start_line=1, end_line=100)
                if f_res.get("status") == "success":
                    evidence_list.append(Evidence(
                        id=f"E{evidence_counter}",
                        type=EvidenceType.FILE,
                        path=clean_ep,
                        line_start=1,
                        line_end=100,
                        content_or_summary=f_res.get("content", ""),
                        source_tool="read_file"
                    ))
                    observations.append(f"Inspected entry point file {clean_ep}.")
                    evidence_counter += 1

    # 4. Search for key terms from bug description
    search_terms = [word for word in case.bug_description.replace(".", " ").replace(",", " ").split() if len(word) > 4 and word.isalnum()]
    for term in search_terms[:3]:
        s_res = search_code(repo_path, term)
        if s_res.get("status") == "success" and s_res.get("matches"):
            matches = s_res["matches"][:3]
            match_summary = "; ".join([f"{m['path']}:{m['line']} ({m['snippet']})" for m in matches])
            evidence_list.append(Evidence(
                id=f"E{evidence_counter}",
                type=EvidenceType.SEARCH,
                content_or_summary=f"Search '{term}' matches: {match_summary}",
                source_tool="search_code"
            ))
            observations.append(f"Found {len(matches)} code occurrences of keyword '{term}'.")
            evidence_counter += 1

    return {
        "evidence": evidence_list,
        "observations": observations
    }
