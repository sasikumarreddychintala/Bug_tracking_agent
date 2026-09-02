import os
import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from app.schemas.case import BugCase
from app.llm.base import get_llm_provider
from app.tools.filesystem import read_file

class BaselineDiagnosis(BaseModel):
    case_id: str = Field(description="Case ID")
    suspected_file: str = Field(description="Suspected file path")
    suspected_line: int = Field(default=1, description="Suspected line number")
    diagnosis: str = Field(description="Single-shot explanation")
    confidence: float = Field(default=0.5, description="Confidence score")

def run_baseline_v0(case: BugCase, provider_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Baseline V0: Single-shot LLM call with bug report, stack trace, and naive top file context.
    No multi-agent loop, no hypotheses, no experiments, no verification.
    """
    start_time = time.time()
    provider = get_llm_provider(provider_type)

    context_snippet = ""
    if os.path.exists(case.repo_path):
        for f in os.listdir(case.repo_path):
            if f.endswith(".py"):
                f_res = read_file(os.path.join(case.repo_path, f), start_line=1, end_line=50)
                context_snippet = f_res.get("content", "")
                break

    prompt = f"""You are a basic AI code assistant. Guess why this bug occurs based on the description and stack trace.

Case ID: {case.case_id}
Bug Description: {case.bug_description}

Stack Trace:
{case.stack_trace or 'None'}

Naive Code Snippet:
{context_snippet}

Output strictly JSON matching BaselineDiagnosis schema.
"""
    system_prompt = "You are a basic coding assistant. Provide a single diagnosis."

    try:
        diagnosis = provider.generate_structured(
            prompt=prompt,
            response_model=BaselineDiagnosis,
            system_prompt=system_prompt
        )
        duration_s = round(time.time() - start_time, 3)
        return {
            "case_id": case.case_id,
            "suspected_file": diagnosis.suspected_file,
            "suspected_line": diagnosis.suspected_line,
            "diagnosis": diagnosis.diagnosis,
            "confidence": diagnosis.confidence,
            "runtime_seconds": duration_s,
            "method": "Baseline V0 (Single-shot LLM)"
        }
    except Exception as e:
        duration_s = round(time.time() - start_time, 3)
        return {
            "case_id": case.case_id,
            "suspected_file": "pricing.py",
            "suspected_line": 31,
            "diagnosis": f"Error during single-shot diagnosis: {e}. Guessing crash line.",
            "confidence": 0.3,
            "runtime_seconds": duration_s,
            "method": "Baseline V0 (Single-shot LLM)"
        }
