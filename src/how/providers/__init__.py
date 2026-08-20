from how.providers.base import LLMProvider
from how.providers.gemini import GeminiProvider
from how.providers.groq import GroqProvider

PROVIDERS: dict[str, type[LLMProvider]] = {
    "Gemini": GeminiProvider,
    "Groq": GroqProvider,
}
