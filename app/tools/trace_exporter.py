import os
import json
from typing import List, Optional
from app.schemas.trace import TraceEvent, InvestigationTraceSummary

def export_trace_to_markdown(
    case_id: str,
    run_id: str,
    events: List[TraceEvent],
    summary: InvestigationTraceSummary,
    output_path: Optional[str] = None
) -> str:
    """
    Exports the complete observable investigation trajectory into a clean,
    human-readable Markdown audit trail document.
    """
    lines = []
    lines.append(f"# 📜 RepoTrace Investigation Audit Trail: `{case_id}`")
    lines.append(f"**Run ID:** `{run_id}` | **Mode:** `{summary.mode}` | **Total Events:** `{len(events)}`\n")
    lines.append("---")
    lines.append("## 📊 Investigation Summary")
    lines.append(f"- **Upstream Root Cause:** `{summary.upstream_root_cause}`")
    lines.append(f"- **Symptom-Trap Avoided:** `{'✅ YES' if summary.symptom_trap_avoided else '❌ NO'}`")
    lines.append(f"- **Tools Used:** `{summary.tools_used_count}`")
    lines.append(f"- **Evidence Items Collected:** `{summary.evidence_collected_count}`")
    lines.append(f"- **Competing Hypotheses Formulated:** `{summary.hypotheses_count}`")
    lines.append(f"- **Controlled Experiments Executed:** `{summary.experiments_count}`")
    lines.append(f"- **Hypotheses Supported:** `{summary.supported_hypotheses_count}` | **Rejected:** `{summary.rejected_hypotheses_count}`")
    lines.append(f"- **Investigation Rounds:** `{summary.investigation_rounds}`")
    lines.append(f"- **Total Runtime:** `{summary.runtime_seconds}s`\n")
    lines.append("---")
    lines.append("## 🧭 Step-by-Step Chronological Trace Timeline\n")

    for idx, ev in enumerate(events, start=1):
        lines.append(f"### `[{idx:02d}]` **{ev.event_type.value}** (`{ev.node}`)")
        lines.append(f"- **Event ID:** `{ev.event_id}` | **Status:** `{ev.status}` | **Timestamp:** `{ev.timestamp}`")
        if ev.tool_name:
            lines.append(f"- **Tool Invoked:** `{ev.tool_name}`")
        if ev.input_summary:
            lines.append(f"- **Input:** {ev.input_summary}")
        if ev.output_summary:
            lines.append(f"- **Observable Output:** {ev.output_summary}")
        if ev.evidence_ids:
            lines.append(f"- **Linked Evidence:** `{', '.join(ev.evidence_ids)}`")
        if ev.hypothesis_ids:
            lines.append(f"- **Linked Hypotheses:** `{', '.join(ev.hypothesis_ids)}`")
        if ev.decision:
            lines.append(f"- **Decision / Result:** **{ev.decision}**")
        lines.append("")

    md_content = "\n".join(lines)

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)

    return md_content

def export_trace_to_json(
    case_id: str,
    run_id: str,
    events: List[TraceEvent],
    summary: InvestigationTraceSummary,
    output_path: Optional[str] = None
) -> str:
    data = {
        "case_id": case_id,
        "run_id": run_id,
        "summary": summary.model_dump(),
        "events_count": len(events),
        "events": [e.model_dump() for e in events]
    }
    json_str = json.dumps(data, indent=2)

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_str)

    return json_str
