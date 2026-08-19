import argparse
import os
import platform
import sys

import questionary
from rich.console import Console

from how.config import ConfigManager
from how.providers import PROVIDERS
from how.providers.base import LLMProvider

PROMPT_TEMPLATE = """
You are a terminal command assistant.

The user is asking questions that should be answered with 
commands that can be executed in their terminal.

Rules:
- Only generate commands that will run on the users operating system.
- To not invent commands or assume software is instaled unless neccessary.
- Return several command options when multiple reasonable approaches exist.
- If the operating system is unknown, assume Debian Linux.
- If the shell is unknown, assume Bash.

User request:
{prompt}

User Environment:
Operating System: {operating_system}
Shell: {shell}

Return the appropriate commands.
"""


def list_supported_providers(provider_index: dict[str, type[LLMProvider]]):

    print("Supported LLM providers:")
    for provider_name in provider_index:
        print(f"  - {provider_name}")


def setup(configurator: ConfigManager):

    # List of all supported provider names
    provider_names = [
        provider_name for provider_name, _ in configurator.provider_index.items()
    ]

    # Prompt user to select an LLM provider
    selected_name = questionary.select(
        "Select an LLM provider to configure:", choices=provider_names
    ).ask()

    # Create provider instance
    provider_class = configurator.provider_index[selected_name]
    provider = provider_class()

    # Authenticate with the LLM provider
    provider.authenticate()

    # Select a model from the provider
    models = provider.get_models()
    selected_model = questionary.select("Select a model:", choices=models).ask()

    # Write provider to config file
    configurator.write_provider(selected_name, selected_model)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--list-supported-providers",
        action="store_true",
        help="List all supported LLM providers",
    )

    parser.add_argument(
        "--setup",
        action="store_true",
        help="Setup an LLM provider",
    )

    parser.add_argument(
        "prompt",
        nargs="?",
        help="Question for the LLM",
    )

    args = parser.parse_args()

    configurator = ConfigManager(PROVIDERS)
    configurator.initialize()

    # List all supported LLM providers
    if args.list_supported_providers:
        list_supported_providers(PROVIDERS)
        sys.exit(0)

    # Setup an LLM provider
    if args.setup:
        setup(configurator)
        sys.exit(0)

    # Instantiate provider
    default_provider_class = configurator.get_default_provider_class()
    if default_provider_class is None:
        print("No LLM provider configured. Run 'how --setup' to configure one.")
        sys.exit(0)
    provider = default_provider_class()

    # Authenticate with the LLM provider
    provider.authenticate()

    # Get model from config
    model = configurator.get_default_provider_model()

    # Get environment information
    operating_system = platform.system()
    shell = os.environ.get("SHELL", "unknown")

    # Construct full prompt
    prompt_with_context = PROMPT_TEMPLATE.format(
        operating_system=operating_system,
        shell=shell,
        prompt=args.prompt,
    )

    console = Console()

    with console.status("[bold green]Working...[/bold green]", spinner="dots"):
        response = provider.generate_commands(prompt_with_context, model)

    options = [o.command for o in response.options]

    choice = questionary.select(
        "Select a command:", choices=[*options, "None / Exit"]
    ).ask()

    print(choice)
