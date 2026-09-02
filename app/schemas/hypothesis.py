from pydantic import BaseModel, Field
from typing import List
from enum import Enum

class HypothesisStatus(str, Enum):
    OPEN = 'open'
    SUPPORTED = 'supported'
    WEAKENED = 'weakened'
    REJECTED = 'rejected'
    UNCERTAIN = 'uncertain'

class Hypothesis(BaseModel):
    id: str = Field(description='Hypothesis ID (e.g. H1)')
    statement: str = Field(description='Root cause explanation statement')
    suspected_locations: List[str] = Field(default_factory=list)
    supporting_evidence: List[str] = Field(default_factory=list)
    contradicting_evidence: List[str] = Field(default_factory=list)
    missing_evidence: List[str] = Field(default_factory=list)
    proposed_experiments: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    status: HypothesisStatus = Field(default=HypothesisStatus.OPEN)
