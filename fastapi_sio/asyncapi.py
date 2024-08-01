from typing import Dict, List, Type
from pydantic import BaseModel
from pydantic.json_schema import models_json_schema

from fastapi_sio.actors import SIOEmitterMeta, SIOHandler
from fastapi_sio.schemas.asyncapi import (
    AsyncAPI,
    AsyncAPIChannel,
    AsyncAPIComponents,
    AsyncAPIIdentifier,
    AsyncAPIInfo,
    AsyncAPIMessage,
    AsyncAPIOperation,
    AsyncAPIServer,
    OpenAPIReference,
)


REF_SCHEMA_TEMPLATE = "#/components/schemas/{model}"


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
        id=AsyncAPIIdentifier(id),
        info=AsyncAPIInfo(
            title=title,
            version=version,
            description=description,
        ),
        servers=servers,
        defaultContentType=defaultContentType,
        channels=get_channels(handlers, emitters),
        operations=get_operations(handlers, emitters),
        components=get_components(used_models),
    )


def get_operations(handlers: List[SIOHandler], emitters: List[SIOEmitterMeta]):
    return {
        handler.event: AsyncAPIOperation(
            action="send",
            channel=OpenAPIReference(**{"$ref": "aaa"}),
            title=handler.name,
            summary=handler.summary,
            description=handler.description,
        )
        for handler in handlers
    } | {
        emitter.event: AsyncAPIOperation(
            action="receive",
            channel=OpenAPIReference(**{"$ref": "aaa"}),
            summary=emitter.summary,
            description=emitter.description,
        )
        for emitter in emitters
    }


def get_channels(
    handlers: List[SIOHandler], emitters: List[SIOEmitterMeta]
) -> dict[str, AsyncAPIChannel]:
    return {
        handler.event: AsyncAPIChannel(
            title=handler.name,
            summary=handler.summary,
            description=handler.description,
            messages={
                handler.event: AsyncAPIMessage(
                    name=handler.name,
                    contentType=handler.media_type,
                    description=handler.message_description,
                    payload=OpenAPIReference(
                        **{
                            "$ref": REF_SCHEMA_TEMPLATE.format(
                                model=handler.model.__name__
                            )
                        }
                    )
                    if handler.model is not None
                    else None,
                )
            },
        )
        for handler in handlers
    } | {
        emitter.event: AsyncAPIChannel(
            summary=emitter.summary,
            description=emitter.description,
            messages={
                emitter.event: AsyncAPIMessage(
                    name=emitter.event,
                    contentType=emitter.media_type,
                    description=emitter.message_description,
                    payload=OpenAPIReference(
                        **{
                            "$ref": REF_SCHEMA_TEMPLATE.format(
                                model=emitter.model.__name__
                            )
                        }
                    )
                    if emitter.model is not None
                    else None,
                )
            },
        )
        for emitter in emitters
    }


def get_components(used_models: List[Type[BaseModel]]) -> AsyncAPIComponents:
    _, schemas = models_json_schema(
        [(model, "validation") for model in used_models],
        ref_template=REF_SCHEMA_TEMPLATE,
    )

    return AsyncAPIComponents(
        schemas=schemas["$defs"],
    )
