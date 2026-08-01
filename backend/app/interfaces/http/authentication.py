from __future__ import annotations

from functools import wraps
from typing import Callable, TypeVar

from flask import current_app, g, request

from app.core.exceptions import AuthenticationError, AuthorizationError
from app.domain.services.auth_service import AuthContext, AuthService

F = TypeVar("F", bound=Callable)


def _authenticate() -> AuthContext:
    existing = getattr(g, "auth_context", None)
    if existing is not None:
        return existing
    header = request.headers.get("Authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise AuthenticationError("A Bearer access token is required.")
    service: AuthService = current_app.extensions["auth_service"]
    context = service.authenticate_access_token(token)
    g.auth_context = context
    return context


def auth_required(function: F) -> F:
    @wraps(function)
    def wrapped(*args, **kwargs):
        _authenticate()
        return function(*args, **kwargs)

    return wrapped  # type: ignore[return-value]


def roles_required(*allowed_roles: str):
    def decorator(function: F) -> F:
        @wraps(function)
        def wrapped(*args, **kwargs):
            context = _authenticate()
            if not set(allowed_roles).intersection(context.roles):
                raise AuthorizationError("You do not have permission to perform this action.")
            return function(*args, **kwargs)

        return wrapped  # type: ignore[return-value]

    return decorator
