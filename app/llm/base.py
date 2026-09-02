import abc
from typing import Type, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class BaseLLMProvider(abc.ABC):
    @abc.abstractmethod
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        pass

    @abc.abstractmethod
    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        max_retries: int = 2,
    ) -> T:
        pass

def get_llm_provider(provider_type: Optional[str] = None) -> BaseLLMProvider:
    from app.config import settings
    provider = provider_type or settings.llm_provider
    if provider == 'openai':
        from app.llm.openai_provider import OpenAIProvider
        return OpenAIProvider()
    elif provider == 'ollama':
        from app.llm.ollama_provider import OllamaProvider
        return OllamaProvider()
    else:
        from app.llm.mock_provider import MockProvider
        return MockProvider()
