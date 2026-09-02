from pydantic import BaseModel, Field
from typing import List, Optional
from app.llm.base import get_llm_provider
from app.schemas.case import BugCase

class BugUnderstandingOutput(BaseModel):
    symptoms: List[str] = Field(description="Symptoms observed")
    known_facts: List[str] = Field(description="Confirmed facts from logs/stacktrace")
    unknowns: List[str] = Field(description="Unknown questions to investigate")
    entry_points: List[str] = Field(description="Initial files to investigate")
    investigation_questions: List[str] = Field(description="Key causal questions")

def run_bug_understanding(case: BugCase, provider_type: Optional[str] = None) -> BugUnderstandingOutput:
    provider = get_llm_provider(provider_type)
    
    prompt = f"""Analyze this software failure report:
Case ID: {case.case_id}
Bug Description: {case.bug_description}

Stack Trace:
{case.stack_trace or 'None provided'}

Logs:
{case.logs or 'None provided'}

Reproduction Command:
{case.reproduction_command or 'None provided'}
"""
    system_prompt = "You are the Bug Understanding Agent for RepoTrace. Return structured symptoms, facts, unknowns, entry points, and questions. Do not determine final root cause."
    
    return provider.generate_structured(
        prompt=prompt,
        response_model=BugUnderstandingOutput,
        system_prompt=system_prompt
    )
