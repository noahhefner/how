import sys

import questionary
from platformdirs import PlatformDirs
from pydantic import ValidationError

from how.models.config import Config
from how.providers.base import LLMProvider
from how.providers.discovery import discover_providers


class ConfigProvider:
    def __init__(self, config_filename: str = "config.json"):

        self.config_filename = config_filename
        self.config: Config | None = None
        self.platform_dirs = PlatformDirs("how", "NoahHefner")
        self.providers_by_name = {provider.provider_name: provider for provider in discover_providers()}

    def load(self) -> Config | None:

        # Config already loaded
        if self.config is not None:
            return self.config

        config_dir = self.platform_dirs.user_config_path
        config_file = config_dir / self.config_filename

        # No config found
        if not config_file.is_file():
            return None

        # Config file exists, load and return
        try:
            self.config = Config.model_validate_json(config_file.read_text())
            return self.config
        except ValidationError as e:
            sys.exit(f"Invalid configuration: {e}")

    def get_provider_class(self) -> type[LLMProvider]:

        if not self.config:
            sys.exit("Config file not loaded.")

        return self.providers_by_name[self.config.provider_name]

    def setup(self) -> None:

        config_dir = self.platform_dirs.user_config_path
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / self.config_filename

        # Delete existing config file
        if config_file.exists():
            config_file.unlink()

        # Prompt user to select an LLM provider
        selected_name = questionary.select(
            "Select LLM provider:", choices=list(self.providers_by_name)
        ).ask()

        # Write new config file
        self.config = Config(provider_name=selected_name)
        config_file.write_text(self.config.model_dump_json(indent=2))

        # Authenticate with selected LLM provider
        provider_class = self.providers_by_name[self.config.provider_name]
        provider = provider_class()
        provider.authenticate(force=True)
