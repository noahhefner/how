from abc import ABC, abstractmethod

from how.models.command import CommandResponse


class LLMProvider(ABC):
    @abstractmethod
    def generate_commands(
        self,
        prompt: str,
        model: str,
    ) -> CommandResponse: ...

    @abstractmethod
    def authenticate(self) -> None: ...

    @abstractmethod
    def get_models(self) -> list[str]: ...
