from how_tui.providers.base import LLMProvider
from how_tui.providers.gemini import GeminiProvider
from how_tui.providers.groq import GroqProvider

PROVIDERS: dict[str, type[LLMProvider]] = {
    "Gemini": GeminiProvider,
    "Groq": GroqProvider,
}
