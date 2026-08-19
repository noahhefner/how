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

    def write_provider(
        self,
        provider_name: str,
        model: str,
        default: bool = False,
    ) -> None:

        provider_config = ProviderConfig(
            provider_name=provider_name,
            default_model=model,
        )

        config_dir = self.platform_dirs.user_config_path
        config_file = config_dir / self.config_filename

        if config_file.exists():
            try:
                self.config = ConfigFile.model_validate_json(config_file.read_text())
            except ValidationError:
                print("Exception while reading config file.", file=sys.stderr)
                sys.exit(1)

            if self.config is not None:
                if self.config.providers is not None:
                    for index, p in enumerate(self.config.providers):
                        if p.provider_name == provider_name:
                            self.config.providers[index] = provider_config
                            config_file.write_text(
                                self.config.model_dump_json(indent=2)
                            )
                            break
                else:
                    self.config = ConfigFile(
                        default_provider=provider_name, providers=[provider_config]
                    )
                    config_file.write_text(self.config.model_dump_json(indent=2))

        else:
            self.config = ConfigFile(
                default_provider=provider_name, providers=[provider_config]
            )
            config_file.write_text(self.config.model_dump_json(indent=2))

    def load(self, force: bool = False) -> ConfigFile | None:
        """Fetches configuration from config file.

        If the configuration file has already been loaded, return the existing configuration. Override this
        behaviour using the force argument.

        If no config file is found, return None.

        If the config file exits, load the configuration data, save it to this ConfigManager instance, and
        return the resulting Config object. Raise an error if the data shape of the config file is malformed.
        """

        # Config already loaded
        if self.config is not None and force is False:
            return self.config

        config_dir = self.platform_dirs.user_config_path
        config_file = config_dir / self.config_filename

        # No config found
        if not config_file.is_file():
            return None

        # Config file exists, load and return
        try:
            self.config = ConfigFile.model_validate_json(config_file.read_text())
            return self.config
        except ValidationError as e:
            # TODO: Print with debug only
            print(f"Invalid configuration file found: {e}", file=sys.stderr)
            raise

    def initialize(self) -> ConfigFile:
        """Create a new config file, deleting the existing file, if one exists."""

        config_dir = self.platform_dirs.user_config_path
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / self.config_filename

        # Delete existing config file
        if config_file.exists():
            config_file.unlink()

        # Write new config file
        self.config = ConfigFile()
        config_file.write_text(self.config.model_dump_json(indent=2))

        return self.config
