import sys
from getpass import getpass

import keyring
from google import genai
from rich.console import Console

from how.models.command import CommandResponse
from how.providers.base import LLMProvider


class GeminiClient(LLMProvider):
    provider_name = "Gemini"

    def __init__(self):

        self.client = None

    def generate_commands(
        self,
        prompt: str,
    ) -> CommandResponse:

        if self.client is None:
            sys.exit("Gemini client not authenticated.")

        interaction = self.client.interactions.create(
            model="gemini-3.5-flash-lite",
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": CommandResponse.model_json_schema(),
            },
        )

        return CommandResponse.model_validate_json(interaction.output_text)

    def authenticate(self, force: bool = False) -> None:

        api_key = keyring.get_password("how", "Gemini")

        if force or api_key is None:

            console = Console()
            console.print("[bold cyan]Gemini configuration[/bold cyan]")

            api_key = getpass("Gemini API key: ")

            if not api_key:
                console.print("[red]API key cannot be empty.[/red]")
                raise SystemExit(1)

            keyring.set_password(
                "how",
                "Gemini",
                api_key
            )

        self.client = genai.Client(api_key=api_key)

