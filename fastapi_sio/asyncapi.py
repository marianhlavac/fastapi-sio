from typing import Dict, List, Type
from pydantic import BaseModel

from pydantic.schema import schema
from fastapi_sio.emitter import SIOEmitterMeta
from fastapi_sio.handler import SIOHandler
from fastapi_sio.schemas.asyncapi import (
    AsyncAPI,
    AsyncAPIChannel,
    AsyncAPIComponents,
    AsyncAPIInfo,
    AsyncAPIMessage,
    AsyncAPIOperation,
    AsyncAPIServer,
    OpenAPIReference,
)


SCHEMA_REF_PREFIX = "#/components/schemas/"


def get_asyncapi(
    id: str,
    title: str,
    version: str,
    description: str,
    servers: Dict[str, AsyncAPIServer],
    handlers: List[SIOHandler],
    emitters: List[SIOEmitterMeta],
    defaultContentType: str = "application/json",
) -> AsyncAPI:
    used_models = [
        handler.model for handler in handlers if handler.model is not None
    ] + [emitter.model for emitter in emitters if emitter.model is not None]

    return AsyncAPI(
        id=id,
        info=AsyncAPIInfo(
            title=title,
            version=version,
            description=description,
        ),
        servers=servers,
        defaultContentType=defaultContentType,
        channels=get_channels(handlers, emitters),
        components=get_components(used_models),
        tags=None,
        externalDocs=None,  # TODO: refer fastapi docs
    )


def get_channels(
    handlers: List[SIOHandler], emitters: List[SIOEmitterMeta]
) -> Dict[str, AsyncAPIChannel]:
    return {
        handler.event: AsyncAPIChannel(
            publish=AsyncAPIOperation(
                operationId=handler.name,
                summary=handler.summary,
                description=handler.description,
                message=AsyncAPIMessage(
                    payload=OpenAPIReference(
                        **{"$ref": f"{SCHEMA_REF_PREFIX}{handler.model.__name__}"}
                    )
                    if handler.model is not None
                    else None,
                ),
            ),
        )
        for handler in handlers
    } | {
        emitter.event: AsyncAPIChannel(
            subscribe=AsyncAPIOperation(
                summary=emitter.summary,
                description=emitter.description,
                message=AsyncAPIMessage(
                    payload=OpenAPIReference(
                        **{"$ref": f"{SCHEMA_REF_PREFIX}{emitter.model.__name__}"}
                    )
                    if emitter.model is not None
                    else None,
                ),
            ),
        )
        for emitter in emitters
    }


def get_components(used_models: List[Type[BaseModel]]) -> AsyncAPIComponents:
    return AsyncAPIComponents(
        schemas=schema(used_models, ref_prefix=SCHEMA_REF_PREFIX)["definitions"],
    )
