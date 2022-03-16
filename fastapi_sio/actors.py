from typing import Any, Generic, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from socketio import AsyncServer
from fastapi.encoders import jsonable_encoder

T = TypeVar("T", bound=BaseModel)


class SIOActorMeta(BaseModel):
    event: str
    title: str | None
    summary: str | None
    description: str | None
    model: Type[BaseModel] | None
    media_type: str
    message_description: str | None


class SIOEmitterMeta(SIOActorMeta):
    # TODO: Currently impossible to import AbstractSetIntStr, MappingIntStrAny
    # from pydantic
    include: Optional[Any] = None
    exclude: Optional[Any] = None
    by_alias: bool = True
    exclude_unset: bool = False
    exclude_defaults: bool = False
    exclude_none: bool = False


class SIOJsonEmitter(Generic[T]):
    def __init__(self, model: Type[T], meta: SIOEmitterMeta, sio: AsyncServer):
        self._meta = meta
        self._model = model
        self._sio = sio

    def get_meta(self):
        return self._meta

    async def emit(self, payload: T, encode_kwargs = {}, **kwargs):
        meta_args = self._meta.dict(
            include={
                "include",
                "exclude",
                "by_alias",
                "exclude_unset",
                "exclude_defaults",
                "exclude_none",
            }
        )

        await self._sio.emit(
            self._meta.event,
            data=jsonable_encoder(payload, **(meta_args | encode_kwargs)),
            **kwargs,
        )


class SIOHandler(SIOActorMeta):
    name: str | None
