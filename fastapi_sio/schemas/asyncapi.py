"""
AsyncAPI 3.0.0

Ref: https://github.com/asyncapi/spec/blob/v3.0.0/spec/asyncapi.md

TODO:
    - Only a short subset of components is supported
"""

from typing import Annotated, Any, Literal, Mapping

from fastapi.openapi.models import (
    Reference as OpenAPIReference,
)
from fastapi.openapi.models import (
    Schema as OpenAPISchema,
)
from pydantic import (
    BaseModel,
    Field,
    RootModel,
    field_validator,
    model_validator,
)

from ..utils import validate_email_address, validate_url_rfc3986

ASYNCAPI_VERSION = "3.0.0"

SecuritySchemeType = (
    Literal["userPassword"]
    | Literal["apiKey"]
    | Literal["X509"]
    | Literal["symmetricEncryption"]
    | Literal["asymmetricEncryption"]
    | Literal["httpApiKey"]
    | Literal["http"]
    | Literal["oauth2"]
    | Literal["openIdConnect"]
    | Literal["plain"]
    | Literal["scramSha256"]
    | Literal["scramSha512"]
    | Literal["gssapi"]
)


class AsyncAPIExternalDocs(BaseModel):
    description: str | None = None
    url: str


class AsyncAPITag(BaseModel):
    name: str
    description: str | None = None
    externalDocs: AsyncAPIExternalDocs | OpenAPIReference | None = None


class AsyncAPIComponents(BaseModel):
    schemas: Mapping[str, OpenAPISchema | OpenAPIReference] | None = None
    # ... TODO!


class AsyncAPIMessageExample(BaseModel):
    headers: Mapping[str, str] | None = None
    payload: Mapping[str, Any] | None = None
    name: str | None = None
    summary: str | None = None


class AsyncAPIMessage(BaseModel):
    headers: OpenAPISchema | OpenAPIReference | None = None
    payload: Any | OpenAPIReference | OpenAPIReference | None = None
    correlationId: Any | None = None  # TODO
    contentType: str | None = None
    name: str | None = None
    title: str | None = None
    summary: str | None = None
    description: str | None = None
    tags: list[AsyncAPITag] | None = None
    externalDocs: AsyncAPIExternalDocs | OpenAPIReference | None = None
    bindings: OpenAPIReference | None = None  # TODO
    examples: list[AsyncAPIMessageExample] | None = None
    traits: OpenAPIReference | None = None  # TODO


class AsyncAPIOneOfMessages(BaseModel):
    oneOf: AsyncAPIMessage | OpenAPIReference


class AsyncAPISecuritySchemeOther(BaseModel):
    type: SecuritySchemeType
    description: str | None = None


class AsyncAPISecuritySchemeHttpApiKey(BaseModel):
    type: SecuritySchemeType = "httpApiKey"
    name: str
    location_in: Annotated[str, Field(alias="in")]


class AsyncAPISecuritySchemeApiKey(BaseModel):
    type: SecuritySchemeType = "apiKey"
    location_in: Annotated[str, Field(alias="in")]


class AsyncAPISecuritySchemeHttp(BaseModel):
    type: SecuritySchemeType = "http"
    scheme: str
    bearerFormat: str | None = None


class AsyncAPISecuritySchemeOAuth2(BaseModel):
    type: SecuritySchemeType = "oauth2"
    flows: Any  # TODO
    scopes: list[str] | None = None


class AsyncAPISecuritySchemeOpenIDConnect(BaseModel):
    type: SecuritySchemeType = "openIdConnect"
    openIdConnectUrl: str
    scopes: list[str] | None = None


AnySecurityScheme = (
    AsyncAPISecuritySchemeOther
    | AsyncAPISecuritySchemeHttpApiKey
    | AsyncAPISecuritySchemeApiKey
    | AsyncAPISecuritySchemeHttp
    | AsyncAPISecuritySchemeOAuth2
    | AsyncAPISecuritySchemeOpenIDConnect
    | OpenAPIReference
)


class AsyncAPIOperation(BaseModel):
    action: Literal["send"] | Literal["receive"]
    channel: OpenAPIReference
    title: str | None = None
    summary: str | None = None
    description: str | None = None
    security: list[AnySecurityScheme] | None = None
    tags: list[AsyncAPITag] | None = None
    externalDocs: AsyncAPIExternalDocs | OpenAPIReference | None = None
    bindings: OpenAPIReference | None = None  # TODO
    traits: OpenAPIReference | None = None  # TODO
    messages: list[OpenAPIReference] | None = None
    reply: OpenAPIReference | None = None  # TODO


class AsyncAPIParameter(BaseModel):
    description: str | None = None
    parameterSchema: Any = Field(..., alias="schema")  # TODO
    location: str | None = None


class AsyncAPIChannel(BaseModel):
    address: str | None = None  # TODO: Add explicit `null` value
    messages: Mapping[str, AsyncAPIMessage | OpenAPIReference] | None = None
    title: str | None = None
    summary: str | None = None
    description: str | None = None
    servers: list[OpenAPIReference] | None = None
    parameters: Mapping[str, AsyncAPIParameter] | None = None
    tags: list[AsyncAPITag] | None = None
    externalDocs: AsyncAPIExternalDocs | OpenAPIReference | None = None
    bindings: OpenAPIReference | None = None  # TODO


class AsyncAPIServerVariable(BaseModel):
    enum: list[str] | None = None
    default: str | None = None
    description: str | None = None
    examples: list[str] | None = None


class AsyncAPIServer(BaseModel):
    host: str
    protocol: str
    protocolVersion: str | None = None
    pathname: str | None = None
    description: str | None = None
    title: str | None = None
    summary: str | None = None
    variables: Mapping[str, AsyncAPIServerVariable | OpenAPIReference] | None = None
    security: list[AnySecurityScheme | OpenAPIReference] | None = None
    tags: list[AsyncAPITag] | None = None
    externalDocs: AsyncAPIExternalDocs | OpenAPIReference | None = None
    bindings: OpenAPIReference | None = None  # TODO


class AsyncAPIInfoLicense(BaseModel):
    name: str
    url: str | None = None


class AsyncAPIInfoContact(BaseModel):
    name: str | None = None
    url: str | None = None
    email: str | None = None

    @field_validator("url")
    def validate_url(cls, v):
        validate_url_rfc3986(v)

    @field_validator("email")
    def validate_email(cls, v):
        validate_email_address(v)


class AsyncAPIInfo(BaseModel):
    title: str
    version: str
    description: str | None = None
    termsOfService: str | None = None
    contact: AsyncAPIInfoContact | None = None
    license: AsyncAPIInfoLicense | None = None
    tags: list[AsyncAPITag] | None = None
    externalDocs: AsyncAPIExternalDocs | OpenAPIReference | None = None


class AsyncAPIIdentifier(RootModel):
    root: str

    @model_validator(mode="after")
    def validate_is_uri(self):
        validate_url_rfc3986(self.root)
        return self


class AsyncAPI(BaseModel):
    asyncapi: str = ASYNCAPI_VERSION
    id: AsyncAPIIdentifier | None = None
    info: AsyncAPIInfo
    servers: Mapping[str, AsyncAPIServer | OpenAPIReference] | None = None
    defaultContentType: str | None = None
    channels: Mapping[str, AsyncAPIChannel | OpenAPIReference]
    operations: Mapping[str, AsyncAPIOperation]
    components: AsyncAPIComponents | None = None
