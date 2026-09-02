from pydantic import BaseModel, Field
from typing import Optional

class ExperimentProposal(BaseModel):
    proposal_id: str = Field(default="EXP-1", description="Proposal ID")
    hypothesis_id: str = Field(default="H1", description="Target Hypothesis ID")
    description: str = Field(default="Run reproduction test in sandbox", description="Description of experiment")
    command: str = Field(default="pytest", description="Command to run")
    expected_outcome_if_true: str = Field(default="")
    expected_outcome_if_false: str = Field(default="")

class ExperimentResult(BaseModel):
    id: str = Field(default="EXP-1", description="Experiment Result ID")
    proposal_id: str = Field(default="EXP-1", description="Proposal ID")
    hypothesis_id: str = Field(default="H1", description="Target hypothesis ID")
    command: str = Field(description="Executed command")
    stdout: str = Field(default="")
    stderr: str = Field(default="")
    exit_code: int = Field(default=0)
    passed: bool = Field(default=True)
    duration_ms: int = Field(default=0)
    evidence_id: Optional[str] = Field(default=None)
