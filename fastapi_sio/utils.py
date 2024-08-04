from email.utils import parseaddr
from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from packaging.version import parse
import re

from pydantic import ValidationError
from rfc3986.validators import Validator
from rfc3986.uri import URIReference
from rfc3986.exceptions import RFC3986Exception

rfc3986_validator = Validator()


def starlette_version() -> tuple[int, int, int]:
    from starlette import __version__

    version = parse(__version__)

    return version.major, version.minor, version.micro


def get_middleware_options(middleware) -> dict[Any, Any]:
    if starlette_version() >= (0, 35, 0):
        return middleware.kwargs
    else:
        return middleware.options


def match_origin(origin: str | None, pattern: str) -> bool:
    """
    Matches origin against a pattern.
    """
    return origin is not None and re.match(pattern, origin) is not None


def find_cors_configuration(app: FastAPI, default: Any) -> Any:
    """
    Looks through FastAPI's middlewares to figure
    out any existing CORS configuration of the parent
    app. Returns [default] if middleware is not found.
    """
    for middleware in app.user_middleware:
        if middleware.cls is not CORSMiddleware:
            continue

        options = get_middleware_options(middleware)
        origins = options.get("allow_origins")
        if origins:
            # Incompatibility fix between CORSMiddleware and python-socketio
            if origins == ["*"]:
                origins = "*"
            return origins

        origins_regex = options.get("allow_origin_regex")
        if origins_regex:
            return lambda origin: match_origin(origin, origins_regex)

    return default


def validate_url_rfc3986(value: str) -> None:
    reference = URIReference.from_string(value)
    try:
        rfc3986_validator.validate(reference)
    except RFC3986Exception:
        raise ValidationError("Values is not a valid RFC3986 URI")


def validate_email_address(value: str):
    parsed_addr = parseaddr(value)
    if parsed_addr == ("", ""):
        raise ValidationError("Wrong e-mail address format")
