import json
import logging
from typing import Type, TypeVar, Optional
from pydantic import BaseModel
from app.llm.base import BaseLLMProvider
from app.config import settings

T = TypeVar('T', bound=BaseModel)
logger = logging.getLogger(__name__)

class OllamaProvider(BaseLLMProvider):
    def __init__(self, model: Optional[str] = None, base_url: Optional[str] = None):
        self.model = model or settings.ollama_model
        self.base_url = base_url or settings.ollama_base_url

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        try:
            import ollama
            client = ollama.Client(host=self.base_url)
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': prompt})
            res = client.chat(model=self.model, messages=messages)
            return res['message']['content']
        except Exception as e:
            logger.warning(f'Ollama call failed: {e}. Fallback to mock.')
            from app.llm.mock_provider import MockProvider
            return MockProvider().generate_text(prompt, system_prompt)

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        max_retries: int = 2,
    ) -> T:
        try:
            system = system_prompt or 'You are an expert software debugging agent.'
            system += f'\nReturn strictly JSON matching schema:\n{json.dumps(response_model.model_json_schema())}'
            raw = self.generate_text(prompt, system_prompt=system)
            clean = raw.strip()
            if clean.startswith('`json'):
                clean = clean[7:]
            if clean.startswith('`'):
                clean = clean[3:]
            if clean.endswith('`'):
                clean = clean[:-3]
            clean = clean.strip()
            data = json.loads(clean)
            return response_model.model_validate(data)
        except Exception as e:
            logger.warning(f'Ollama structured parse failed: {e}. Fallback to mock.')
            from app.llm.mock_provider import MockProvider
            return MockProvider().generate_structured(prompt, response_model, system_prompt)
