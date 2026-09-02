from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
import datetime

class EvidenceType(str, Enum):
    FILE = 'file'
    SEARCH = 'search'
    STACKTRACE = 'stacktrace'
    LOG = 'log'
    TEST = 'test'
    COMMAND = 'command'
    AST = 'ast'
    GIT = 'git'

class Evidence(BaseModel):
    id: str = Field(description='Evidence ID (e.g. E1)')
    type: EvidenceType = Field(description='Type of evidence')
    path: Optional[str] = Field(default=None, description='File path')
    line_start: Optional[int] = Field(default=None, description='Start line number')
    line_end: Optional[int] = Field(default=None, description='End line number')
    content_or_summary: str = Field(description='Content or summary')
    code_snippet: Optional[str] = Field(default=None, description='Extracted code snippet if any')
    command: Optional[str] = Field(default=None)
    exit_code: Optional[int] = Field(default=None)
    source_tool: str = Field(description='Originating tool')
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
