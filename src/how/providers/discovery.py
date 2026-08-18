import importlib
import inspect
import pkgutil

import how.providers
from how.providers.base import LLMProvider


def discover_providers() -> list[type[LLMProvider]]:
    providers = []

    for module_info in pkgutil.iter_modules(how.providers.__path__):
        if module_info.name in {"base", "discovery"}:
            continue

        module = importlib.import_module(f"how.providers.{module_info.name}")

        for _, cls in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(cls, LLMProvider)
                and cls is not LLMProvider
                and cls.__module__ == module.__name__
            ):
                providers.append(cls)

    return providers
