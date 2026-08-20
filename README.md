# how

A terminal command assistant that uses LLMs to generate shell commands from natural language questions. Ask it how to do something and it will suggest commands for your specific OS and shell.

## Features

- Ask natural-language questions and get relevant terminal commands
- Interactive selection menu to choose from multiple command suggestions
- OS and shell aware — generates commands specific to your environment
- Pluggable LLM provider system — easily add new providers
- Authentication credentials stored securely in your OS keyring
- Structured output via Pydantic for reliable command parsing
- Selectable models for configured LLM providers

## Installation

```bash
# Clone the repository
git clone https://github.com/nhefner/how.git
cd how

# Install with uv (recommended)
uv sync

# Or install with pip
pip install .
```

### Requirements

- Python >= 3.14
- An API key for a supported LLM provider (currently Google Gemini)

## Usage

### First-time setup

```bash
how --setup
```

This will walk you through selecting a provider and authenticating with your API key.

### Ask a question

```bash
how "compress a folder"
how "find all files larger than 100MB"
how "list all running docker containers"
how "rename multiple files at once"
```

### List Supported LLM Providers

```bash
how --list-supported-providers
```

### Run without installing

```bash
uv run how "find largest file in the /opt directory"
```

## Roadmap

1. **Logs** — Add configurable logging for debugging provider interactions, request/response payloads, and errors.
2. **Tests** — Add a comprehensive test suite covering CLI behavior, provider integration, config management, and command parsing.
3. **Descriptions for each command** — Display a short explanation alongside each suggested command so users understand what it does before selecting.
4. **Install script** — Provide a standalone install script (`install.sh`) that sets up the tool without requiring the user to manually manage Python environments.
5. **Shell wrapper** — A shell function or script that, after the user selects a command and `how` exits, places that command directly on the command line (ready to edit or press Enter to execute) rather than just printing it to stdout.
6. **More LLM Providers** - Add support for more LLM providers.

## Supported Providers

| Provider | Status |
|----------|--------|
| Google Gemini | Supported |

### Adding a New LLM Provider

Drop a new Python file in `src/how/providers/` with a class that subclasses `LLMProvider`:

```python
from how.providers.base import LLMProvider


class MyProvider(LLMProvider):
    def generate_commands(
        self,
        prompt: str,
        model: str,
    ) -> CommandResponse: ...

    def authenticate(self) -> None: ...

    def get_models(self) -> list[str]: ...
```

The provider will be automatically discovered on the next run.

## License

MIT