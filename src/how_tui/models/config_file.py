"""
Expected layout of the configuration file.
"""

from pydantic import BaseModel, Field


class ConfigFile(BaseModel):
    default_provider: str | None = None
    # Key: Provider Name, Value: Provider Details
    providers: dict[str, ProviderConfig] = Field(default_factory=dict)


class ProviderConfig(BaseModel):
    model: str
