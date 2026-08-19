from pydantic import BaseModel


class ConfigFile(BaseModel):
    default_provider: str | None = None
    providers: list[ProviderConfig] | None = None


class ProviderConfig(BaseModel):
    provider_name: str
    default_model: str
