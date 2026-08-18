from abc import ABC, abstractmethod

from how.models.command import CommandResponse


class LLMProvider(ABC):
    provider_name: str

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not getattr(cls, "provider_name", None):
            raise TypeError(f"{cls.__name__} must define provider_name")

    @abstractmethod
    def generate_commands(
        self,
        prompt: str,
    ) -> CommandResponse: ...


    @abstractmethod
    def authenticate(self) -> None: ...