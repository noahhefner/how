import argparse
import logging
import os
import platform
import sys

import questionary
from rich.console import Console

from how_tui.config import ConfigManager
from how_tui.providers import PROVIDERS

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

logger = logging.getLogger(__name__)


def list_supported_providers(configurator: ConfigManager):
    """List all LLM providers that are supported by how-tui."""

    print("Supported LLM providers:")
    for provider_name in configurator.provider_index:
        print(f"  - {provider_name}")


def list_configured_providers(configurator: ConfigManager):
    """List all LLM providers that the user has configured."""

    assert configurator.config is not None
    assert configurator.config.providers is not None

    if len(configurator.config.providers) == 0:
        print("No providers configured.")
        return

    print("Configured LLM providers:")
    for provider_name in configurator.config.providers:
        print(f"  - {provider_name}")


def remove_provider(configurator: ConfigManager):
    """Remove an LLM provider.

    Removes the provider from the configuration file and erases locally stored
    auth credentials.
    """

    assert configurator.config is not None
    assert configurator.config.providers is not None

    provider_names = list(configurator.config.providers.keys())
    if len(provider_names) == 0:
        print("No providers configured. Run 'how --setup' to configure a provider.")
        return

    # Prompt user to select an LLM provider to remove
    selected_name = questionary.select(
        "Select an LLM provider to remove:", choices=provider_names
    ).ask()

    # Get provider class
    provider = configurator.provider_index[selected_name]

    # Unauthenticate with the LLM provider
    provider.unauthenticate()

    # Remove from the config file
    configurator.remove_provider(selected_name)


def set_default_provider(configurator: ConfigManager):
    """Set a default LLM provider."""

    assert configurator.config is not None

    if configurator.config.providers is None:
        print("No providers configured. Run 'how --setup' to configure a provider.")
        return

    provider_names = list(configurator.config.providers.keys())

    # Prompt user to select a default provider
    selected_name = questionary.select(
        "Select a default LLM provider:", choices=provider_names
    ).ask()

    # Update config
    configurator.set_default_provider(selected_name)


def add_provider(configurator: ConfigManager):
    """Configure an LLM provider."""

    # List of all supported provider names
    provider_names = [
        provider_name for provider_name, _ in configurator.provider_index.items()
    ]

    # Prompt user to select an LLM provider
    selected_name = questionary.select(
        "Select an LLM provider to configure:", choices=provider_names
    ).ask()

    # Get provider class
    provider = configurator.provider_index[selected_name]
    assert provider is not None

    # Authenticate with the LLM provider
    provider.authenticate()

    # Select a model from the provider
    models = provider.get_models()
    selected_model = questionary.select("Select a model:", choices=models).ask()

    # Write provider to config file
    configurator.add_provider(selected_name, selected_model)


def print_commands(commands: list[str]):
    """Display commands reccommended by the AI."""

    print("Command suggestions:")
    for command in commands:
        print(f"  - {command}")


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--list-supported-providers",
        action="store_true",
        help="List all supported LLM providers",
    )

    parser.add_argument(
        "--list-configured-providers",
        action="store_true",
        help="List your configured LLM providers",
    )

    parser.add_argument(
        "--add-provider",
        action="store_true",
        help="Setup an LLM provider",
    )

    parser.add_argument(
        "--remove-provider",
        action="store_true",
        help="Remove an LLM provider",
    )

    parser.add_argument(
        "--set-default-provider",
        action="store_true",
        help="Set a default LLM provider",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug level logging",
    )

    parser.add_argument(
        "prompt",
        nargs="?",
        help="Question for the LLM",
    )

    args = parser.parse_args()

    # Configure log level
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Get environment information
    operating_system = platform.system()
    shell = os.environ.get("SHELL", "unknown")
    logger.debug(f"Detected operating system: {operating_system}")
    logger.debug(f"Detected shell: {shell}")

    # Create config manager
    configurator = ConfigManager(PROVIDERS)
    configurator.initialize()

    # List all supported LLM providers
    if args.list_supported_providers:
        list_supported_providers(configurator)
        sys.exit(0)

    # List users configured LLM providers
    if args.list_configured_providers:
        list_configured_providers(configurator)
        sys.exit(0)

    # Remove a configured LLM provider
    if args.remove_provider:
        remove_provider(configurator)
        sys.exit(0)

    # Set a default provider
    if args.set_default_provider:
        set_default_provider(configurator)
        sys.exit(0)

    # Add an LLM provider
    if args.add_provider:
        add_provider(configurator)
        sys.exit(0)

    # No prompt
    if args.prompt is None or args.prompt.strip() == "":
        parser.print_help()
        sys.exit(0)

    # Get provider
    provider = configurator.get_default_provider_class()
    if provider is None:
        print("No LLM provider configured. Run 'how --setup' to configure one.")
        sys.exit(0)

    # Authenticate with the LLM provider
    provider.authenticate()

    # Get model from config
    model = configurator.get_default_provider_model()

    # Construct full prompt
    prompt_with_context = PROMPT_TEMPLATE.format(
        operating_system=operating_system,
        shell=shell,
        prompt=args.prompt,
    )

    # Get commands from the AI
    console = Console()
    try:
        with console.status("[bold green]Working...[/bold green]", spinner="dots"):
            response = provider.generate_commands(prompt_with_context, model)
    except Exception:  # noqa: BLE001
        console.print("[red]An error occurred while generating commands.[/red]")
        sys.exit(1)

    # Print commands to the console
    commands = [c.command for c in response.commands]
    print_commands(commands)
