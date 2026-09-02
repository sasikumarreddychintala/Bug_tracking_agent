from pydantic import BaseModel, Field
from typing import List
from enum import Enum

class VerificationDecision(str, Enum):
    SUPPORTED = 'SUPPORTED'
    WEAKENED = 'WEAKENED'
    REJECTED = 'REJECTED'
    UNCERTAIN = 'UNCERTAIN'

class Verification(BaseModel):
    hypothesis_id: str = Field(description='Hypothesis ID')
    decision: VerificationDecision = Field(description='Verification decision')
    reasoning: str = Field(description='Detailed reasoning')
    is_upstream_cause: bool = Field(default=False)
    is_symptom_only: bool = Field(default=False)
    evidence_ids: List[str] = Field(default_factory=list)
    experiment_ids: List[str] = Field(default_factory=list)
