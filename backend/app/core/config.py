from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from dotenv import load_dotenv


def _bool(value: str | bool | None, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"Invalid Boolean value: {value!r}")


def _int(value: str | int | None, default: int, *, minimum: int = 0) -> int:
    parsed = default if value is None else int(value)
    if parsed < minimum:
        raise ValueError(f"Expected an integer greater than or equal to {minimum}.")
    return parsed


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str
    environment: str
    debug: bool
    secret_key: str
    cors_origins: tuple[str, ...]
    database_url: str
    db_pool_size: int
    db_max_overflow: int
    db_pool_recycle_seconds: int
    db_echo: bool
    redis_url: str
    jwt_secret: str
    jwt_algorithm: str
    jwt_issuer: str
    jwt_audience: str
    jwt_access_expire_minutes: int
    jwt_refresh_expire_days: int
    jwt_leeway_seconds: int
    jwt_refresh_cookie_name: str
    jwt_refresh_cookie_secure: bool
    jwt_refresh_cookie_samesite: str
    jwt_refresh_cookie_path: str
    otp_expire_seconds: int
    otp_resend_cooldown_seconds: int
    otp_max_attempts: int
    otp_max_requests_per_hour: int
    otp_length: int
    otp_development_mode: bool
    password_min_length: int
    data_encryption_key: str
    dev_admin_first_name: str
    dev_admin_last_name: str
    dev_admin_email: str
    dev_admin_phone: str | None
    dev_admin_password: str

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    def flask_mapping(self) -> dict[str, Any]:
        values = asdict(self)
        values.update(
            {
                "APP_NAME": self.app_name,
                "ENVIRONMENT": self.environment,
                "DEBUG": self.debug,
                "SECRET_KEY": self.secret_key,
                "DATABASE_URL": self.database_url,
                "REDIS_URL": self.redis_url,
                "JSON_SORT_KEYS": False,
                "JSON_AS_ASCII": False,
            }
        )
        return values


_PLACEHOLDERS = {
    "",
    "change-this-secret",
    "change-this-jwt-secret",
    "replace-with-valid-encryption-key",
    "change-this-password",
}


def load_settings(env_file: str | Path | None = None) -> Settings:
    """Load and validate process configuration at the single dotenv boundary."""

    path = Path(env_file) if env_file else Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(path, override=False)

    db_user = os.getenv("DB_USER", "neurotech_user")
    db_password = os.getenv("DB_PASS", "neurotech_pass")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = _int(os.getenv("DB_PORT"), 3306, minimum=1)
    db_name = os.getenv("DB_NAME", "neurotech_db")
    database_url = os.getenv(
        "DATABASE_URL",
        (
            f"mysql+mysqlconnector://{quote_plus(db_user)}:{quote_plus(db_password)}"
            f"@{db_host}:{db_port}/{quote_plus(db_name)}"
            "?charset=utf8mb4&collation=utf8mb4_unicode_ci"
        ),
    )

    settings = Settings(
        app_name=os.getenv("APP_NAME", "NeuroTech Backend"),
        environment=os.getenv("FLASK_ENV", "development"),
        debug=_bool(os.getenv("FLASK_DEBUG"), True),
        secret_key=os.getenv("SECRET_KEY", "change-this-secret"),
        cors_origins=tuple(
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
            if origin.strip()
        ),
        database_url=database_url,
        db_pool_size=_int(os.getenv("DB_POOL_SIZE"), 10, minimum=1),
        db_max_overflow=_int(os.getenv("DB_MAX_OVERFLOW"), 20),
        db_pool_recycle_seconds=_int(os.getenv("DB_POOL_RECYCLE_SECONDS"), 1800),
        db_echo=_bool(os.getenv("DB_ECHO"), False),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        jwt_secret=os.getenv("JWT_SECRET", "change-this-jwt-secret"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        jwt_issuer=os.getenv("JWT_ISSUER", "neurotech"),
        jwt_audience=os.getenv("JWT_AUDIENCE", "neurotech-users"),
        jwt_access_expire_minutes=_int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES"), 15, minimum=1),
        jwt_refresh_expire_days=_int(os.getenv("JWT_REFRESH_EXPIRE_DAYS"), 30, minimum=1),
        jwt_leeway_seconds=_int(os.getenv("JWT_LEEWAY_SECONDS"), 10),
        jwt_refresh_cookie_name=os.getenv("JWT_REFRESH_COOKIE_NAME", "neurotech_refresh_token"),
        jwt_refresh_cookie_secure=_bool(os.getenv("JWT_REFRESH_COOKIE_SECURE"), False),
        jwt_refresh_cookie_samesite=os.getenv("JWT_REFRESH_COOKIE_SAMESITE", "Lax"),
        jwt_refresh_cookie_path=os.getenv("JWT_REFRESH_COOKIE_PATH", "/auth"),
        otp_expire_seconds=_int(os.getenv("OTP_EXPIRE_SECONDS"), 120, minimum=30),
        otp_resend_cooldown_seconds=_int(os.getenv("OTP_RESEND_COOLDOWN_SECONDS"), 60),
        otp_max_attempts=_int(os.getenv("OTP_MAX_ATTEMPTS"), 5, minimum=1),
        otp_max_requests_per_hour=_int(os.getenv("OTP_MAX_REQUESTS_PER_HOUR"), 5, minimum=1),
        otp_length=_int(os.getenv("OTP_LENGTH"), 6, minimum=4),
        otp_development_mode=_bool(os.getenv("OTP_DEVELOPMENT_MODE"), True),
        password_min_length=_int(os.getenv("PASSWORD_MIN_LENGTH"), 8, minimum=8),
        data_encryption_key=os.getenv("DATA_ENCRYPTION_KEY", "replace-with-valid-encryption-key"),
        dev_admin_first_name=os.getenv("DEV_ADMIN_FIRST_NAME", "Development"),
        dev_admin_last_name=os.getenv("DEV_ADMIN_LAST_NAME", "Admin"),
        dev_admin_email=os.getenv("DEV_ADMIN_EMAIL", "admin@example.com"),
        dev_admin_phone=os.getenv("DEV_ADMIN_PHONE") or None,
        dev_admin_password=os.getenv("DEV_ADMIN_PASSWORD", "change-this-password"),
    )
    _validate(settings)
    return settings


def _validate(settings: Settings) -> None:
    if settings.jwt_algorithm not in {"HS256", "HS384", "HS512"}:
        raise ValueError("JWT_ALGORITHM must be an explicitly supported HMAC algorithm.")
    if settings.jwt_refresh_cookie_samesite not in {"Lax", "Strict", "None"}:
        raise ValueError("JWT_REFRESH_COOKIE_SAMESITE must be Lax, Strict, or None.")
    if settings.is_production:
        secrets = {
            "SECRET_KEY": settings.secret_key,
            "JWT_SECRET": settings.jwt_secret,
            "DATA_ENCRYPTION_KEY": settings.data_encryption_key,
            "DEV_ADMIN_PASSWORD": settings.dev_admin_password,
        }
        invalid = [name for name, value in secrets.items() if value in _PLACEHOLDERS]
        if invalid:
            raise ValueError(f"Production configuration contains placeholder values: {', '.join(invalid)}")
        if len(settings.secret_key) < 32 or len(settings.jwt_secret) < 32:
            raise ValueError("Production application and JWT secrets must be at least 32 characters.")
        try:
            from cryptography.fernet import Fernet

            Fernet(settings.data_encryption_key.encode("ascii"))
        except (ValueError, TypeError) as exc:
            raise ValueError("DATA_ENCRYPTION_KEY must be a valid Fernet key.") from exc
        if not settings.jwt_refresh_cookie_secure:
            raise ValueError("Production refresh cookies must be Secure.")
        if settings.otp_development_mode:
            raise ValueError("OTP development mode must be disabled in Production.")
        if "neurotech_pass" in settings.database_url:
            raise ValueError("Production database credentials must not use development defaults.")
