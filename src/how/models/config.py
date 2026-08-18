from pydantic import BaseModel


class Config(BaseModel):
    provider_name: str
