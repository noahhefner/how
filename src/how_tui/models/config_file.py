"""
Expected layout of the configuration file.
"""

from pydantic import BaseModel


class ConfigFile(BaseModel):
    default_provider: str | None = None
    # Key: Provider Name, Value: Provider Details
    providers: dict[str, ProviderConfig] | None = None


class ProviderConfig(BaseModel):
    model: str
