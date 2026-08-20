import json
import sys
from getpass import getpass

import groq.types
import keyring
from groq import Groq
from rich.console import Console

from how.models.command import CommandResponse
from how.providers.base import LLMProvider


class GroqProvider(LLMProvider):
    @staticmethod
    def generate_commands(
        prompt: str,
        model: str,
    ) -> CommandResponse:

        client = GroqProvider._get_client()

        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "terminal_commands",
                "strict": True,
                "schema": CommandResponse.model_json_schema(),
            },
        }

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format=response_format,
        )

        result = json.loads(response.choices[0].message.content or "{}")
        if not result:
            print("An error occurred.")
            sys.exit(1)

        return CommandResponse.model_validate(result)

    @staticmethod
    def authenticate(force: bool = False) -> None:

        api_key = keyring.get_password("how", "Groq")

        if force or api_key is None:
            console = Console()

            api_key = getpass("Groq API key: ")

            if not api_key:
                console.print("[red]API key cannot be empty.[/red]")
                sys.exit(1)

            keyring.set_password("how", "Groq", api_key)

    @staticmethod
    def unauthenticate() -> None:
        """Clear local credentials."""

        api_key = keyring.get_password("how", "Groq")

        if api_key is None:
            print("No API key found for Groq.")
            return

        keyring.delete_password("how", "Groq")

    @staticmethod
    def get_models() -> list[str]:
        """Get all Groq models via the API.

        Requires authentication to list models.
        """

        client = GroqProvider._get_client()
        models: groq.types.ModelListResponse = client.models.list()

        return [m.id for m in models.data]

    @staticmethod
    def _get_client() -> Groq:
        """Create and return a Groq client.

        Assumptions:
            - User is authenticated.
        """

        api_key = keyring.get_password("how", "Groq")
        if api_key is None:
            print("Groq not authenticated.", file=sys.stderr)
            sys.exit(1)

        return Groq(api_key=api_key)
