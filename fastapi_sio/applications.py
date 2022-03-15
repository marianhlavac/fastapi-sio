from asyncio import AbstractEventLoop
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel
import socketio
from fastapi import FastAPI

from fastapi_sio.asyncapi import get_asyncapi
from fastapi_sio.actors import SIOJsonEmitter, SIOEmitterMeta, SIOHandler
from fastapi_sio.schemas.asyncapi import AsyncAPI, AsyncAPIServer
from fastapi_sio.utils import find_cors_configuration

T = TypeVar("T", bound=BaseModel)

# Following props are directly proxied to socketio.AsyncServer
# from FastAPISIO instances
# TODO: Probs not possible to have static analysis working

PROXIED_PROPS = [
    "attach",
    "send",
    "call",
    "close_room",
    "get_session",
    "save_session",
    "session",
    "disconnect",
    "handle_request",
    "start_background_task",
    "sleep",
    "enter_room",
    "leave_room",
]


class FastAPISIO:
    def __init__(
        self,
        app: FastAPI,
        mount_location: str = "/sio",
        socketio_path: str = "socket.io",
        async_mode: str = "asgi",
        asyncapi_url: str | None = "/sio/docs",
        version: str | None = None,
        other_asgi_app = None,
        servers: Dict[str, AsyncAPIServer] | None = None,
        loop: AbstractEventLoop | None = None,
        monitor_clients: bool = True,
    ):
        self._sio = socketio.AsyncServer(
            async_mode=async_mode,
            cors_allowed_origins=find_cors_configuration(app, default=[]),
            monitor_clients=monitor_clients,
            loop=loop,
        )
        self._asgiapp = socketio.ASGIApp(
            socketio_server=self._sio,
            socketio_path=socketio_path,
            other_asgi_app=other_asgi_app,
        )
        self._app = app
        self._handlers: List[SIOHandler] = []
        self._emitters: List[SIOJsonEmitter] = []
        self._servers = servers

        self.asyncapi_schema: AsyncAPI | None = None
        self.asyncapi_url = asyncapi_url
        self.version = version

        # self.make_props_proxies()

        if asyncapi_url is not None:
            self._app.get(
                asyncapi_url + "/asyncapi.json",
                include_in_schema=False,
                response_model=AsyncAPI,
                response_model_exclude_none=True,
            )(self.asyncapi)

        app.mount(mount_location, self._asgiapp)
        app.state.sio = self._sio

    def asyncapi(self) -> AsyncAPI:
        if not self.asyncapi_schema:
            self.asyncapi_schema = get_asyncapi(
                id="urn:com:" + "_".join(self._app.title.lower().split(" ")),
                title=self._app.title,
                version=self.version or self._app.version,
                description=self._app.description,
                servers=self._servers or {},
                handlers=self._handlers,
                emitters=[emitter.get_meta() for emitter in self._emitters],
            )
        return self.asyncapi_schema

    def on(
        self,
        event: str,
        title: str | None = None,
        summary: str | None = None,
        description: str | None = None,
        message_description: str | None = None,
        model: Type[BaseModel] | None = None,
        media_type: str = "application/json",
    ) -> Callable:
        def decorator(fn: Callable):
            self._handlers.append(
                SIOHandler(
                    name=fn.__name__,
                    event=event,
                    title=title,
                    summary=summary,
                    description=description,
                    model=model,
                    media_type=media_type,
                    message_description=message_description,
                )
            )
            self._sio.on(event=event, handler=fn)

        return decorator

    def create_emitter(
        self,
        event: str,
        model: Type[T],
        title: str | None = None,
        summary: str | None = None,
        description: str | None = None,
        message_description: str | None = None,
        media_type: str = "application/json",
        include: Optional[Any] = None,
        exclude: Optional[Any] = None,
        by_alias: bool = True,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> SIOJsonEmitter[T]:
        emitter = SIOJsonEmitter(
            model=model,
            meta=SIOEmitterMeta(
                event=event,
                title=title,
                summary=summary,
                description=description,
                model=model,
                media_type=media_type,
                message_description=message_description,
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
            ),
            sio=self._sio,
        )
        self._emitters.append(emitter)
        return emitter

    @property
    def connect(self):
        def decorator(fn: Callable):
            self._sio.on("connect", handler=fn)
        return decorator

    @property
    def attach(self):
        return self._sio.attach

    @property
    def close_room(self):
        return self._sio.close_room

    @property
    def get_session(self):
        return self._sio.get_session

    @property
    def save_session(self):
        return self._sio.save_session

    @property
    def session(self):
        return self._sio.session

    @property
    def disconnect(self):
        return self._sio.disconnect

    @property
    def handle_request(self):
        return self._sio.handle_request

    @property
    def start_background_task(self):
        return self._sio.start_background_task

    @property
    def sleep(self):
        return self._sio.sleep

    @property
    def enter_room(self):
        return self._sio.enter_room

    @property
    def leave_room(self):
        return self._sio.leave_room

    @property
    def rooms(self):
        return self._sio.rooms
