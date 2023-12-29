from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import re


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

        origins = middleware.options.get("allow_origins")
        if origins:
            # Incompatibility fix between CORSMiddleware and python-socketio
            if origins == ["*"]:
                origins = "*"
            return origins

        origins_regex = middleware.options.get("allow_origin_regex")
        if origins_regex:
            return lambda origin: match_origin(origin, origins_regex)

    return default
