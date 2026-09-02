from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
import datetime

class TraceEventType(str, Enum):
    CASE_STARTED = "CASE_STARTED"
    REPOSITORY_LOADED = "REPOSITORY_LOADED"
    FAILURE_DISCOVERY_STARTED = "FAILURE_DISCOVERY_STARTED"
    FAILURE_DISCOVERY_COMPLETED = "FAILURE_DISCOVERY_COMPLETED"
    STACKTRACE_PARSED = "STACKTRACE_PARSED"
    TOOL_CALL = "TOOL_CALL"
    TOOL_RESULT = "TOOL_RESULT"
    EVIDENCE_ADDED = "EVIDENCE_ADDED"
    EVIDENCE_VALIDATED = "EVIDENCE_VALIDATED"
    HYPOTHESIS_CREATED = "HYPOTHESIS_CREATED"
    HYPOTHESIS_UPDATED = "HYPOTHESIS_UPDATED"
    EXPERIMENT_SELECTED = "EXPERIMENT_SELECTED"
    EXPERIMENT_STARTED = "EXPERIMENT_STARTED"
    EXPERIMENT_COMPLETED = "EXPERIMENT_COMPLETED"
    VERIFICATION = "VERIFICATION"
    ROOT_CAUSE_SELECTED = "ROOT_CAUSE_SELECTED"
    REPORT_GENERATED = "REPORT_GENERATED"
    CASE_COMPLETED = "CASE_COMPLETED"
    ERROR = "ERROR"

class TraceEvent(BaseModel):
    event_id: str = Field(description="Unique event ID, e.g. E-001")
    run_id: str = Field(description="Run ID")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    node: str = Field(description="Graph node or agent producing this event")
    event_type: TraceEventType = Field(description="Explicit event type")
    tool_name: Optional[str] = Field(default=None, description="Tool called if applicable")
    input_summary: Optional[str] = Field(default=None, description="Observable action input summary")
    output_summary: Optional[str] = Field(default=None, description="Observable output summary")
    evidence_ids: List[str] = Field(default_factory=list, description="Linked Evidence IDs")
    hypothesis_ids: List[str] = Field(default_factory=list, description="Linked Hypothesis IDs")
    decision: Optional[str] = Field(default=None, description="Verification or routing decision")
    duration_ms: Optional[int] = Field(default=None, description="Action duration in ms")
    status: str = Field(default="success", description="Status: success, rejected, failed, error")

class InvestigationTraceSummary(BaseModel):
    case_id: str
    run_id: str
    mode: str = "MODE_A_KNOWN_FAILURE"
    tools_used_count: int
    evidence_collected_count: int
    hypotheses_count: int
    experiments_count: int
    supported_hypotheses_count: int
    rejected_hypotheses_count: int
    investigation_rounds: int
    runtime_seconds: float
    upstream_root_cause: str
    symptom_trap_avoided: bool = True
