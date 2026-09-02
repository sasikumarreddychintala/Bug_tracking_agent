from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.schemas.evidence import Evidence

class Report(BaseModel):
    case_id: str = Field(description='Case ID')
    diagnosis: str = Field(description='Executive diagnosis')
    root_cause_file: str = Field(description='Root cause file')
    root_cause_lines: str = Field(description='Root cause lines')
    root_cause_summary: str = Field(description='Root cause summary')
    mechanism: str = Field(description='Causal mechanism')
    evidence_chain: List[Evidence] = Field(default_factory=list)
    reproduction_status: str = Field(default='PASS')
    reproduction_details: str = Field(default='')
    hypotheses_evaluation: List[Dict[str, Any]] = Field(default_factory=list)
    recommended_fix: str = Field(description='Fix recommendation')
    regression_test: str = Field(description='Regression test')
    confidence: str = Field(default='HIGH')
    limitations: str = Field(default='')
    runtime_seconds: float = Field(default=0.0)
