from pydantic import BaseModel


class CommandOption(BaseModel):
    command: str


class CommandResponse(BaseModel):
    options: list[CommandOption]
