from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from packaging.version import parse
import re


def starlette_version() -> tuple[int, int, int]:
    from starlette import __version__

    version = parse(__version__)

    return version.major, version.minor, version.micro


def get_middleware_options(middleware):
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
