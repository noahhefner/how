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

    def _check_client(self):

        if self.client is None:
            print("Gemini client not authenticated.", file=sys.stderr)
            sys.exit(1)

    def generate_commands(
        self,
        prompt: str,
        model: str,
    ) -> CommandResponse:

        self._check_client()

        interaction = self.client.interactions.create(
            model=model,
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
                sys.exit(1)

            keyring.set_password("how", "Gemini", api_key)

        self.client = genai.Client(api_key=api_key)

    def get_models(self) -> list[str]:

        self._check_client()

        return [m.name for m in self.client.models.list()]
