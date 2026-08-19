from how.providers.base import LLMProvider
from how.providers.gemini import GeminiProvider

PROVIDERS: dict[str, type[LLMProvider]] = {"Gemini": GeminiProvider}
