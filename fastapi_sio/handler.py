from typing import Type
from pydantic import BaseModel


class SIOHandler(BaseModel):
    event: str
    name: str | None
    title: str | None
    summary: str | None
    description: str | None
    model: Type[BaseModel] | None
    media_type: str
