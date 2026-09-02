from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class BugCase(BaseModel):
    case_id: str = Field(description='Unique case identifier, e.g. BUG-001')
    repo_path: str = Field(description='Local path or URL to repository')
    commit_sha: Optional[str] = Field(default=None, description='Commit hash')
    bug_description: str = Field(description='Summary of the bug symptoms')
    stack_trace: Optional[str] = Field(default=None, description='Raw stack trace')
    logs: Optional[str] = Field(default=None, description='Application logs')
    reproduction_command: Optional[str] = Field(default=None, description='Reproduction command')
    environment_info: Optional[Dict[str, Any]] = Field(default_factory=dict)
