from __future__ import annotations

from typing import Any


class AppError(Exception):
    status_code = 400
    code = "application_error"

    def __init__(self, message: str, *, errors: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.errors = errors


class ValidationAppError(AppError):
    status_code = 422
    code = "validation_error"


class AuthenticationError(AppError):
    status_code = 401
    code = "authentication_error"


class AuthorizationError(AppError):
    status_code = 403
    code = "authorization_error"


class DuplicateResourceError(AppError):
    status_code = 409
    code = "duplicate_resource"


class ResourceNotFoundError(AppError):
    status_code = 404
    code = "not_found"


class TokenError(AuthenticationError):
    code = "invalid_token"


class TokenReuseDetected(TokenError):
    code = "refresh_token_reuse"


class OtpError(AppError):
    code = "otp_error"


class OtpRateLimitError(OtpError):
    status_code = 429
    code = "otp_rate_limited"


class OtpCooldownError(OtpRateLimitError):
    code = "otp_resend_cooldown"


class OtpAttemptsExceeded(OtpError):
    status_code = 429
    code = "otp_attempts_exceeded"


class InfrastructureError(AppError):
    status_code = 503
    code = "dependency_unavailable"
