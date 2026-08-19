import argparse
import os
import platform

import sys
import questionary
from rich.console import Console

from how.config import ConfigProvider

from how.providers.discovery import discover_providers

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

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "prompt", 
        help="Question for the LLM",
        nargs="*",
    )

    parser.add_argument(
        "--list-providers",
        action="store_true",
        help="List supported LLM providers",
    )

    parser.add_argument(
        "--setup",
        action="store_true",
        help="Configure an LLM provider"
    )
    
    args = parser.parse_args()
    
    if args.list_providers:
        print("Supported LLM providers:")
        for provider in discover_providers():
            print(f"  - {provider.provider_name}")
        return

    configurator = ConfigProvider()

    if args.setup:
        configurator.setup()
        return

    config = configurator.load()
    if not config:
        sys.exit("Config file not found. Run how --setup to configure an LLM provider.")

    provider_class = configurator.get_provider_class()
    provider = provider_class()

    prompt = " ".join(args.prompt)

    operating_system = platform.system()
    shell = os.environ.get("SHELL", "unknown")
    
    prompt_with_context = PROMPT_TEMPLATE.format(
        operating_system=operating_system,
        shell=shell,
        prompt=prompt,
    )

    console = Console()

    with console.status("[bold green]Working...[/bold green]", spinner="dots"):
        response = provider.generate_commands(prompt_with_context)

    options = [o.command for o in response.options]

    choice = questionary.select(
        "Select a command:",
        choices = [*options, "None / Exit"]
    ).ask()

    print(choice)