import json
import logging
from typing import Type, TypeVar, Optional
from pydantic import BaseModel
from app.llm.base import BaseLLMProvider
from app.config import settings

T = TypeVar('T', bound=BaseModel)
logger = logging.getLogger(__name__)

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        self.model = model or settings.openai_model
        api_key = api_key or settings.openai_api_key
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except Exception as e:
            logger.warning(f'OpenAI init error: {e}. Falling back to mock.')
            self.client = None

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.client:
            from app.llm.mock_provider import MockProvider
            return MockProvider().generate_text(prompt, system_prompt)
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1
        )
        return response.choices[0].message.content or ''

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        max_retries: int = 2,
    ) -> T:
        if not self.client:
            from app.llm.mock_provider import MockProvider
            return MockProvider().generate_structured(prompt, response_model, system_prompt)
            
        system = system_prompt or 'You are an expert software root-cause analysis agent.'
        system += f'\nReturn strictly JSON matching schema:\n{json.dumps(response_model.model_json_schema())}'
        
        for attempt in range(max_retries + 1):
            try:
                content = self.generate_text(prompt, system_prompt=system)
                clean = content.strip()
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
                logger.warning(f'Structured parse retry {attempt+1}: {e}')
        
        from app.llm.mock_provider import MockProvider
        return MockProvider().generate_structured(prompt, response_model, system_prompt)
