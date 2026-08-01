from __future__ import annotations

from flask import Flask
from marshmallow import ValidationError
from redis import RedisError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions import AppError
from app.core.responses import error_response


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ValidationError)
    def handle_validation(error: ValidationError):
        return error_response("Validation failed.", errors=error.messages, status=422)

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        return error_response(error.message, errors=error.errors, status=error.status_code)

    @app.errorhandler(IntegrityError)
    def handle_integrity(error: IntegrityError):
        return error_response("The request conflicts with an existing resource.", status=409)

    @app.errorhandler(RedisError)
    def handle_redis(error: RedisError):
        return error_response("A required service is temporarily unavailable.", status=503)

    @app.errorhandler(SQLAlchemyError)
    def handle_database(error: SQLAlchemyError):
        return error_response("A database operation could not be completed.", status=503)

    @app.errorhandler(Exception)
    def handle_unexpected(error: Exception):
        app.logger.exception("Unhandled request failure")
        return error_response("An unexpected error occurred.", status=500)
