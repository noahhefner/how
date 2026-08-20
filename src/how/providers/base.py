from abc import ABC, abstractmethod

from how.models.command import CommandResponse


class LLMProvider(ABC):
    @staticmethod
    @abstractmethod
    def generate_commands(
        prompt: str,
        model: str,
    ) -> CommandResponse: ...

    @staticmethod
    @abstractmethod
    def authenticate(force: bool = False) -> None: ...

    @staticmethod
    @abstractmethod
    def unauthenticate() -> None: ...

    @staticmethod
    @abstractmethod
    def get_models() -> list[str]: ...
