from typing import Generic, Type, TypeVar
from pydantic import BaseModel
from socketio import AsyncServer

T = TypeVar("T", bound=BaseModel)


class SIOEmitterMeta(BaseModel):
    event: str
    title: str | None
    summary: str | None
    description: str | None
    model: Type[BaseModel] | None
    media_type: str


class SIOJsonEmitter(Generic[T]):
    def __init__(self, model: Type[T], meta: SIOEmitterMeta, sio: AsyncServer):
        self._meta = meta
        self._model = model
        self._sio = sio

    def get_meta(self):
        return self._meta

    async def emit(self, payload: T):
        await self._sio.emit(self._meta.event, data=payload.json())
