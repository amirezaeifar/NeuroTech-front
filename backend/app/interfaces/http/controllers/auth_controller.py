from __future__ import annotations

from typing import Any

from flask import Blueprint, g, request

from app.core.config import Settings
from app.core.exceptions import AuthenticationError
from app.core.responses import success_response
from app.domain.services.auth_service import AuthService, ClientContext
from app.domain.services.otp_service import OtpService
from app.interfaces.http.authentication import auth_required
from app.interfaces.http.schemas.auth_schemas import (
    ChangePasswordSchema,
    LoginSchema,
    OtpRequestSchema,
    OtpVerifySchema,
    RegisterSchema,
)


def create_auth_blueprint(
    auth_service: AuthService, otp_service: OtpService, settings: Settings
) -> Blueprint:
    blueprint = Blueprint("auth", __name__, url_prefix="/auth")

    @blueprint.post("/register")
    def register():
        values = RegisterSchema().load(request.get_json(silent=True) or {})
        user = auth_service.register(values)
        return success_response(user, message="Registration completed.", status=201)

    @blueprint.post("/login")
    def login():
        values = LoginSchema().load(request.get_json(silent=True) or {})
        result = auth_service.login(values["identifier"], values["password"], _client())
        return _session_response(result, settings, message="Authentication succeeded.")

    @blueprint.post("/request-otp")
    def request_otp():
        values = OtpRequestSchema().load(request.get_json(silent=True) or {})
        data = otp_service.request_otp(values["destination"], values["purpose"])
        return success_response(data, message="If delivery is available, a verification code was sent.")

    @blueprint.post("/verify-otp")
    def verify_otp():
        values = OtpVerifySchema().load(request.get_json(silent=True) or {})
        result = otp_service.verify_otp(
            values["destination"], values["purpose"], values["code"], _client()
        )
        if "refresh_token" in result:
            return _session_response(result, settings, message="Verification succeeded.")
        return success_response(result, message="Verification succeeded.")

    @blueprint.post("/refresh")
    def refresh_session():
        token = request.cookies.get(settings.jwt_refresh_cookie_name)
        if not token:
            raise AuthenticationError("A refresh-token cookie is required.")
        result = auth_service.refresh_session(token, _client())
        return _session_response(result, settings, message="Session refreshed.")

    @blueprint.post("/logout")
    def logout():
        auth_service.logout(request.cookies.get(settings.jwt_refresh_cookie_name))
        response, status = success_response({}, message="Logged out.")
        _clear_refresh_cookie(response, settings)
        return response, status

    @blueprint.post("/logout-all")
    @auth_required
    def logout_all():
        auth_service.logout_all(g.auth_context.user_public_id)
        response, status = success_response({}, message="All sessions were revoked.")
        _clear_refresh_cookie(response, settings)
        return response, status

    @blueprint.get("/me")
    @auth_required
    def me():
        user = auth_service.get_current_user(g.auth_context.user_public_id)
        return success_response(user)

    @blueprint.post("/change-password")
    @auth_required
    def change_password():
        values = ChangePasswordSchema().load(request.get_json(silent=True) or {})
        auth_service.change_password(
            g.auth_context.user_public_id,
            values["current_password"],
            values["new_password"],
        )
        response, status = success_response(
            {}, message="Password changed. Authenticate again with the new password."
        )
        _clear_refresh_cookie(response, settings)
        return response, status

    return blueprint


def _client() -> ClientContext:
    return ClientContext(
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string if request.user_agent else None,
    )


def _session_response(result: dict[str, Any], settings: Settings, *, message: str):
    data = dict(result)
    refresh_token = data.pop("refresh_token")
    refresh_expires_at = data.pop("refresh_token_expires_at", None)
    response, status = success_response(data, message=message)
    response.set_cookie(
        settings.jwt_refresh_cookie_name,
        refresh_token,
        httponly=True,
        secure=settings.jwt_refresh_cookie_secure,
        samesite=settings.jwt_refresh_cookie_samesite,
        path=settings.jwt_refresh_cookie_path,
        max_age=settings.jwt_refresh_expire_days * 86400,
    )
    return response, status


def _clear_refresh_cookie(response, settings: Settings) -> None:
    response.delete_cookie(
        settings.jwt_refresh_cookie_name,
        path=settings.jwt_refresh_cookie_path,
        secure=settings.jwt_refresh_cookie_secure,
        httponly=True,
        samesite=settings.jwt_refresh_cookie_samesite,
    )
