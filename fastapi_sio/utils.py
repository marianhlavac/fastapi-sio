from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def find_cors_configuration(app: FastAPI, default: Any) -> Any:
    """
    Looks through FastAPI's middlewares to figure
    out any existing CORS configuration of the parent
    app. Returns [default] if middleware is not found.
    """
    for middleware in app.user_middleware:
        if middleware.cls is not CORSMiddleware:
            continue

        return middleware.options.get("allow_origins")

    return default
