import sys
from getpass import getpass

import keyring
from google import genai
from google.genai.pagers import Pager
from rich.console import Console

from how_tui.models.command import CommandResponse
from how_tui.providers.base import LLMProvider


class GeminiProvider(LLMProvider):
    @staticmethod
    def generate_commands(
        prompt: str,
        model: str,
    ) -> CommandResponse:
        """Send request to Gemini.

        Response format is specified in the request.

        Assumptions:
            - User is authenticated.
        """

        client = GeminiProvider._get_client()

        interaction = client.interactions.create(
            model=model,
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": CommandResponse.model_json_schema(),
            },
        )

        return CommandResponse.model_validate_json(interaction.output_text)  # ty: ignore[invalid-argument-type, unresolved-attribute]

    @staticmethod
    def authenticate(force: bool = False) -> None:
        """Authenticate with Google Gemini via API key.

        API key is securely stored via keyring.

        Use the force argument to overwrite existing API key.
        """

        api_key = keyring.get_password("how-tui", "Gemini")

        if force or api_key is None:
            console = Console()

            api_key = getpass("Gemini API key: ")

            if not api_key:
                console.print("[red]API key cannot be empty.[/red]")
                sys.exit(1)

            keyring.set_password("how-tui", "Gemini", api_key)

    @staticmethod
    def unauthenticate() -> None:
        """Clear local credentials."""

        api_key = keyring.get_password("how-tui", "Gemini")

        if api_key is None:
            print("No API key found for Gemini.")
            return

        keyring.delete_password("how-tui", "Gemini")

    @staticmethod
    def get_models() -> list[str]:
        """Get all Gemini models via the API.

        Requires authentication to list models.
        """

        client = GeminiProvider._get_client()
        models: Pager = client.models.list()
        return [m.name for m in list(models)]

    @staticmethod
    def _get_client() -> genai.Client:
        """Create and return a Gemini client.

        Assumptions:
            - User is authenticated.
        """

        api_key = keyring.get_password("how-tui", "Gemini")
        if api_key is None:
            print("Gemini not authenticated.", file=sys.stderr)
            sys.exit(1)

        return genai.Client(api_key=api_key)
