from pydantic import BaseModel, ConfigDict


class CommandOption(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command: str


class CommandResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    commands: list[CommandOption]
