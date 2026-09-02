import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    max_investigation_rounds: int = int(os.getenv("REPOTRACE_MAX_ROUNDS", "5"))
    sandbox_timeout_seconds: int = int(os.getenv("SANDBOX_TIMEOUT", "30"))
    reports_dir: str = os.getenv("REPORTS_DIR", "reports")
    trajectories_dir: str = os.getenv("TRAJECTORIES_DIR", "trajectories")

settings = Settings()
