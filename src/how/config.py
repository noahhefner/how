import sys

from platformdirs import PlatformDirs
from pydantic import ValidationError

from how.models.config_file import ConfigFile, ProviderConfig
from how.providers.base import LLMProvider


class ConfigManager:
    def __init__(
        self,
        provider_index: dict[str, type[LLMProvider]],
        config_filename: str = "config.json",
    ):

        self.config_filename = config_filename
        self.config: ConfigFile | None = None
        self.platform_dirs = PlatformDirs("how", "NoahHefner")
        self.provider_index = provider_index

    def initialize(self):
        """Create or load configuration file."""

        config_dir = self.platform_dirs.user_config_path
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / self.config_filename

        if not config_file.exists():
            self._create_config_file(config_file)
            return

        if not config_file.is_file():
            print("Config file is not a file.", file=sys.stderr)
            sys.exit(1)

        self._load_config_file(config_file)

    def write_provider(
        self,
        provider_name: str,
        model: str,
        default: bool = False,
    ) -> None:
        """Write LLM provider data to config file.

        Assumptions:
            - Configuration file exists.
            - Configuration file data has been read into this class via initialize function.
        """

        assert self.config is not None

        provider_config = ProviderConfig(
            model=model,
        )

        # Update internal state
        if self.config.providers is None:
            self.config.providers = {
                provider_name: provider_config,
            }
        else:
            self.config.providers[provider_name] = provider_config
        if default or self.config.default_provider is None:
            self.config.default_provider = provider_name

        # Update config file on disk
        config_dir = self.platform_dirs.user_config_path
        config_file = config_dir / self.config_filename

        assert config_file.exists()
        assert config_file.is_file()

        config_file.write_text(self.config.model_dump_json(indent=2))

    def get_default_provider_class(self) -> type[LLMProvider] | None:

        assert self.config is not None

        if self.config.default_provider is None:
            return None

        default_provider_class = self.provider_index[self.config.default_provider]
        if default_provider_class is None:
            print(
                f"Invalid default provider: {self.config.default_provider}",
                file=sys.stderr,
            )
            sys.exit(1)

        return default_provider_class

    def get_default_provider_model(self) -> str:

        assert self.config is not None
        assert self.config.default_provider is not None
        assert self.config.providers is not None

        default_provider = self.config.providers[self.config.default_provider]
        assert default_provider is not None

        model = default_provider.model
        if model is None:
            print("Model not configured for default LLM provider.", file=sys.stderr)
            sys.exit(1)

        return model

    def _create_config_file(self, config_file) -> None:
        """Create a new, empty config file."""

        self.config = ConfigFile()
        config_file.write_text(self.config.model_dump_json(indent=2))

    def _load_config_file(self, config_file) -> None:
        """Read config file data into this class instance.

        Assumptions:
            - Configuration file exists.
        """

        assert config_file.exists()
        assert config_file.is_file()

        try:
            self.config = ConfigFile.model_validate_json(config_file.read_text())
        except ValidationError:
            print("Invalid configuration file.", file=sys.stderr)
            sys.exit(1)
