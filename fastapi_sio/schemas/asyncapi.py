"""
AsyncAPI 2.4.0

Ref: https://github.com/asyncapi/spec/blob/v2.4.0/spec/asyncapi.md

TODO:
    - Only a short subset of components is supported
"""

ASYNCAPI_VERSION = "2.4.0"

from typing import Any, Dict, List
from pydantic import BaseModel, Field
from fastapi.openapi.models import (
    Schema as OpenAPISchema,
    Reference as OpenAPIReference,
)


class AsyncAPIInfoContact(BaseModel):
    name: str | None = None
    url: str | None = None
    email: str | None = None


class AsyncAPIInfoLicense(BaseModel):
    name: str
    url: str | None = None


class AsyncAPIInfo(BaseModel):
    title: str
    version: str
    description: str | None = None
    termsOfService: str | None = None
    contact: AsyncAPIInfoContact | None = None
    license: AsyncAPIInfoLicense | None = None


class AsyncAPIServer(BaseModel):
    url: str
    protocol: str
    protocolVersion: str | None = None
    description: str | None = None
    variables: Dict[str, Any] | None = None  # TODO
    security: List[Any] | None = None  # TODO
    bindings: Any | None = None  # TODO


class AsyncAPIExternalDocs(BaseModel):
    description: str | None = None
    url: str


class AsyncAPITag(BaseModel):
    name: str
    description: str | None = None
    externalDocs: AsyncAPIExternalDocs | None = None


class AsyncAPIMessage(BaseModel):
    payload: Any | None = None
    headers: OpenAPISchema | OpenAPIReference | None = None
    correlationId: Any | None = None  # TODO
    schemaFormat: str | None = None
    contentType: str | None = None
    name: str | None = None
    title: str | None = None
    summary: str | None = None
    description: str | None = None
    tags: List[AsyncAPITag] | None = None
    externalDocs: AsyncAPIExternalDocs | None = None
    bindings: Any | None = None  # TODO
    examples: List[Any] | None = None  # TODO
    traits: Any | None = None  # TODO


class AsyncAPIOneOfMessages(BaseModel):
    oneOf: AsyncAPIMessage | OpenAPIReference


class AsyncAPIOperation(BaseModel):
    operationId: str | None = None
    summary: str | None = None
    description: str | None = None
    tags: List[AsyncAPITag] | None = None
    externalDocs: AsyncAPIExternalDocs | None = None
    bindings: Any | None = None  # TODO
    traits: Any | None = None  # TODO
    message: AsyncAPIMessage | AsyncAPIOneOfMessages | OpenAPIReference


class AsyncAPIParameter(BaseModel):
    description: str | None = None
    parameterSchema: Any = Field(..., alias="schema")  # TODO
    location: str | None = None


class AsyncAPIChannel(BaseModel):
    description: str | None = None
    servers: List[str] | None = None
    subscribe: AsyncAPIOperation | None = None
    publish: AsyncAPIOperation | None = None
    parameters: Dict[str, AsyncAPIParameter] | None = None
    bindings: Any | None = None  # TODO


class AsyncAPIComponents(BaseModel):
    schemas: Dict[str, OpenAPISchema | OpenAPIReference] | None = None


class AsyncAPI(BaseModel):
    asyncapi: str = ASYNCAPI_VERSION
    id: str | None = None
    info: AsyncAPIInfo
    servers: Dict[str, AsyncAPIServer] | None = None
    defaultContentType: str | None = None
    channels: Dict[str, AsyncAPIChannel]
    components: AsyncAPIComponents | None = None
    tags: List[AsyncAPITag] | None = None
    externalDocs: AsyncAPIExternalDocs | None = None
