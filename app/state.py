from typing import TypedDict, List, Dict, Any, Optional
from app.schemas.case import BugCase
from app.schemas.evidence import Evidence
from app.schemas.hypothesis import Hypothesis
from app.schemas.experiment import ExperimentProposal, ExperimentResult
from app.schemas.verification import Verification
from app.schemas.report import Report
from app.schemas.trace import TraceEvent, InvestigationTraceSummary

class InvestigationState(TypedDict, total=False):
    # Operating Mode
    mode: str  # "MODE_A_KNOWN_FAILURE" or "MODE_B_DISCOVER_FAILURES"

    # Context & Case Definition
    run_id: str
    case: Optional[BugCase]
    repo_path: str
    commit_sha: Optional[str]

    # Mode B Discovered Failures
    discovered_failures: List[Dict[str, Any]]
    failure_clusters: List[Dict[str, Any]]
    selected_failure_id: Optional[str]

    # Bug Understanding Stage
    symptoms: List[str]
    known_facts: List[str]
    unknowns: List[str]
    entry_points: List[str]
    investigation_questions: List[str]

    # Investigation & Code Retrieval Stage
    repo_summary: Dict[str, Any]
    file_tree: List[Dict[str, Any]]
    stacktrace_frames: List[Dict[str, Any]]
    evidence: List[Evidence]
    observations: List[str]

    # Hypothesis Generation Stage
    hypotheses: List[Hypothesis]

    # Experimentation & Reproduction Stage
    experiment_proposals: List[ExperimentProposal]
    experiments: List[ExperimentResult]

    # Verification Stage
    verifications: List[Verification]
    is_root_cause_found: bool

    # Evidence Validation & Hallucination Guard
    evidence_validation_passed: bool
    evidence_validation_details: List[Dict[str, Any]]

    # Final Synthesis & First-Class Trace
    report: Optional[Report]
    trace_events: List[TraceEvent]
    trace_summary: Optional[InvestigationTraceSummary]
    trajectory: List[Dict[str, Any]]

    # Graph Control & Safety
    investigation_round: int
    max_rounds: int
    is_finished: bool
    error_message: Optional[str]
