from __future__ import annotations

from dataclasses import replace
from typing import Any

import click
from flask import Flask
from flask_cors import CORS

from app.core.config import Settings, load_settings
from app.domain.ports.clock import SystemClock
from app.domain.services.auth_service import AuthService
from app.domain.services.health_service import HealthService
from app.domain.services.otp_service import OtpService
from app.infrastructure.db.maria_engine import create_database_engine
from app.infrastructure.db.session import create_session_registry
from app.infrastructure.db.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.health import RedisHealthProbe, SqlAlchemyHealthProbe
from app.infrastructure.otp.development_otp_sender import DevelopmentOtpSender
from app.infrastructure.redis.otp_store import RedisOtpStore
from app.infrastructure.redis.redis_client import create_redis_client
from app.infrastructure.security.pyjwt_token_service import PyJwtTokenService
from app.infrastructure.security.werkzeug_password_hasher import WerkzeugPasswordHasher
from app.interfaces.http.controllers.auth_controller import create_auth_blueprint
from app.interfaces.http.controllers.health_controller import create_health_blueprint
from app.interfaces.http.error_handlers import register_error_handlers


def create_app(config_override: dict | None = None) -> Flask:
    """Flask Application Factory and the only dependency-composition boundary."""

    overrides = dict(config_override or {})
    settings = _settings_with_overrides(load_settings(overrides.pop("ENV_FILE", None)), overrides)
    app = Flask(__name__)
    app.config.update(settings.flask_mapping())
    app.config.update({key: value for key, value in overrides.items() if key.isupper()})

    CORS(
        app,
        origins=settings.cors_origins,
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
    )

    engine = overrides.get("ENGINE") or create_database_engine(settings)
    session_registry = overrides.get("SESSION_REGISTRY") or create_session_registry(engine)
    redis_client = overrides.get("REDIS_CLIENT") or create_redis_client(settings.redis_url)
    clock = overrides.get("CLOCK") or SystemClock()
    password_hasher = overrides.get("PASSWORD_HASHER") or WerkzeugPasswordHasher()
    token_service = overrides.get("TOKEN_SERVICE") or PyJwtTokenService(
        settings.jwt_secret,
        settings.jwt_algorithm,
        settings.jwt_issuer,
        settings.jwt_audience,
        settings.jwt_access_expire_minutes,
        settings.jwt_refresh_expire_days,
        settings.jwt_leeway_seconds,
        clock,
    )
    uow_factory = overrides.get("UOW_FACTORY") or (
        lambda: SqlAlchemyUnitOfWork(session_registry)
    )
    auth_service = overrides.get("AUTH_SERVICE") or AuthService(
        uow_factory,
        password_hasher,
        token_service,
        clock,
        password_min_length=settings.password_min_length,
    )
    otp_store = overrides.get("OTP_STORE") or RedisOtpStore(redis_client)
    otp_sender = overrides.get("OTP_SENDER") or DevelopmentOtpSender()
    otp_service = overrides.get("OTP_SERVICE") or OtpService(
        otp_store,
        otp_sender,
        clock,
        auth_service,
        hash_secret=settings.secret_key,
        expire_seconds=settings.otp_expire_seconds,
        resend_cooldown_seconds=settings.otp_resend_cooldown_seconds,
        max_attempts=settings.otp_max_attempts,
        max_requests_per_hour=settings.otp_max_requests_per_hour,
        code_length=settings.otp_length,
        development_mode=settings.otp_development_mode,
    )
    health_service = overrides.get("HEALTH_SERVICE") or HealthService(
        [SqlAlchemyHealthProbe(engine), RedisHealthProbe(redis_client)]
    )

    app.extensions.update(
        {
            "settings": settings,
            "database_engine": engine,
            "session_registry": session_registry,
            "redis_client": redis_client,
            "auth_service": auth_service,
            "otp_service": otp_service,
            "health_service": health_service,
            "token_service": token_service,
        }
    )
    app.register_blueprint(create_auth_blueprint(auth_service, otp_service, settings))
    app.register_blueprint(create_health_blueprint(health_service, settings))
    register_error_handlers(app)
    _register_cli(app, auth_service, settings)

    @app.teardown_appcontext
    def cleanup_session(exception: BaseException | None = None) -> None:
        session_registry.remove()

    return app


def _settings_with_overrides(settings: Settings, overrides: dict[str, Any]) -> Settings:
    mapping = {
        field: overrides[field.upper()]
        for field in settings.__dataclass_fields__
        if field.upper() in overrides
    }
    return replace(settings, **mapping) if mapping else settings


def _register_cli(app: Flask, auth_service: AuthService, settings: Settings) -> None:
    @app.cli.command("create-roles")
    def create_roles_command() -> None:
        roles = auth_service.create_default_roles()
        click.echo(f"Roles ready: {', '.join(roles)}")

    @app.cli.command("create-admin")
    @click.option("--first-name", default=None)
    @click.option("--last-name", default=None)
    @click.option("--email", default=None)
    @click.option("--phone", default=None)
    @click.option("--password", default=None, hide_input=True)
    def create_admin_command(
        first_name: str | None,
        last_name: str | None,
        email: str | None,
        phone: str | None,
        password: str | None,
    ) -> None:
        resolved_password = password or settings.dev_admin_password
        if settings.is_production and not password:
            raise click.UsageError("Production admin creation requires --password.")
        user = auth_service.create_admin(
            {
                "first_name": first_name or settings.dev_admin_first_name,
                "last_name": last_name or settings.dev_admin_last_name,
                "email": email or settings.dev_admin_email,
                "phone": phone or settings.dev_admin_phone,
                "password": resolved_password,
                "preferred_locale": "fa",
            }
        )
        click.echo(f"Admin ready: {user['public_id']}")
