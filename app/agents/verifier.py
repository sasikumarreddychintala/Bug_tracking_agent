from pydantic import BaseModel, Field
from typing import List, Optional
from app.llm.base import get_llm_provider
from app.schemas.hypothesis import Hypothesis
from app.schemas.experiment import ExperimentResult
from app.schemas.evidence import Evidence
from app.schemas.verification import Verification

class VerificationsOutput(BaseModel):
    verifications: List[Verification] = Field(description="Verification assessments for each hypothesis")

def run_verification(
    hypotheses: List[Hypothesis],
    evidence_list: Optional[List[Evidence]] = None,
    experiments: Optional[List[ExperimentResult]] = None,
    provider_type: Optional[str] = None,
    evidence: Optional[List[Evidence]] = None
) -> List[Verification]:
    evidence_items = evidence if evidence is not None else (evidence_list or [])
    exp_list = experiments or []
    provider = get_llm_provider(provider_type)

    hypo_str = "\n".join([f"- [{h.id}] {h.statement} (Locations: {', '.join(h.suspected_locations)})" for h in hypotheses])
    exp_str = "\n".join([f"- [{e.proposal_id}] Cmd: '{e.command}' | ExitCode: {e.exit_code} | Passed: {e.exit_code == 0} | Stdout snippet: {e.stdout[:200]}" for e in exp_list])
    evi_str = "\n".join([f"- [{e.id}] ({e.type.value}) {e.content_or_summary[:120]}" for e in evidence_items])

    prompt = f"""Critically verify each competing hypothesis using evidence and experiment results:

Hypotheses:
{hypo_str}

Experiment Execution:
{exp_str}

Evidence:
{evi_str}

For each hypothesis:
1. Determine decision: SUPPORTED, WEAKENED, REJECTED, or UNCERTAIN.
2. Differentiate whether the hypothesis identifies the UPSTREAM ROOT CAUSE or merely the DOWNSTREAM SYMPTOM.
3. Reference specific Evidence IDs and Experiment IDs.
"""
    system_prompt = "You are the independent Verification Agent for RepoTrace. Challenge hypotheses objectively and reject symptom-only or disproven explanations."

    res = provider.generate_structured(
        prompt=prompt,
        response_model=VerificationsOutput,
        system_prompt=system_prompt
    )
    return res.verifications
