from pydantic import BaseModel, Field
from typing import List, Optional
from app.llm.base import get_llm_provider
from app.schemas.evidence import Evidence
from app.schemas.hypothesis import Hypothesis
from app.schemas.case import BugCase

class HypothesesOutput(BaseModel):
    hypotheses: List[Hypothesis] = Field(description="2-4 competing root cause hypotheses")

def run_hypothesis_generation(
    case: BugCase,
    evidence_list: Optional[List[Evidence]] = None,
    observations: Optional[List[str]] = None,
    provider_type: Optional[str] = None,
    evidence: Optional[List[Evidence]] = None
) -> List[Hypothesis]:
    evidence_items = evidence if evidence is not None else (evidence_list or [])
    obs_list = observations or []
    provider = get_llm_provider(provider_type)

    evidence_str = "\n".join([f"- [{e.id}] ({e.type.value}) {e.path or 'repo'}:{e.line_start or ''} - {e.content_or_summary[:150]}" for e in evidence_items])
    obs_str = "\n".join([f"- {o}" for o in obs_list])

    prompt = f"""Based on the evidence gathered for {case.case_id}, formulate 2 to 4 competing root-cause hypotheses (H1, H2, H3).

Bug Description:
{case.bug_description}

Observations:
{obs_str}

Evidence Items:
{evidence_str}

Generate competing hypotheses exploring:
1. Primary upstream logic defect / validation omission / state corruption
2. Downstream component defect / symptom site
3. Test fixture / harness or environment issue

Output strict JSON matching HypothesesOutput schema.
"""
    system_prompt = "You are the Hypothesis Generation Agent for RepoTrace. Formulate distinct competing hypotheses with evidence links and experiment proposals. Do not confirm any hypothesis."

    res = provider.generate_structured(
        prompt=prompt,
        response_model=HypothesesOutput,
        system_prompt=system_prompt
    )
    return res.hypotheses
