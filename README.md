# how-tui

A terminal command assistant that uses LLMs to generate shell commands from natural language questions. Ask it how to do something and it will suggest commands for your specific OS and shell.

## Features

- Ask natural-language questions and get relevant terminal command suggestions
- OS and shell aware — generates commands specific to your environment
- Pluggable LLM provider system — easily add new providers
- Authentication credentials stored securely in your OS keyring
- Structured output via Pydantic for reliable command parsing
- Selectable models for configured LLM providers

## Installation

Install `how-tui` with `uv`:

```sh
uv tool install how-tui
```

### Requirements

- Python >= 3.14
- An API key for a supported LLM provider

## Usage

```sh
$ how
usage: how [-h] [--list-supported-providers] [--list-configured-providers] [--add-provider]
           [--remove-provider] [--set-default-provider]
           [prompt]

positional arguments:
  prompt                Question for the LLM

options:
  -h, --help            show this help message and exit
  --list-supported-providers
                        List all supported LLM providers
  --list-configured-providers
                        List your configured LLM providers
  --add-provider        Setup an LLM provider
  --remove-provider     Remove an LLM provider
  --set-default-provider
                        Remove an LLM provider
```

### First-Time Setup

```bash
how --add-provider
```

This will walk you through selecting an LLM provider and authenticating.

### Ask a question

```bash
how "compress a folder"
how "find all files larger than 100MB"
how "list all running docker containers"
how "rename multiple files at once"
```

## Roadmap

1. **Logs** — Add configurable logging for debugging provider interactions, request/response payloads, and errors.
2. **Tests** — Add a comprehensive test suite covering CLI behavior, provider integration, config management, and command parsing.
3. **Descriptions for each command** — Display a short explanation alongside each suggested command so users understand what it does before selecting.
4. **More LLM Providers** - Add support for more LLM providers.

## Supported Providers

| Provider | Status |
|----------|--------|
| Google Gemini | Supported |
| Groq | Supported |

### Adding a New LLM Provider

Drop a new Python file in `src/how_tui/providers/` with a class that subclasses `LLMProvider`:

```python
from abc import ABC, abstractmethod

from how_tui.models.command import CommandResponse


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

```

## License

MIT