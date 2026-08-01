from __future__ import annotations

import hashlib
import hmac
import uuid
from datetime import timedelta, timezone
from typing import Any

import jwt

from app.core.exceptions import TokenError
from app.domain.ports.clock import Clock
from app.domain.ports.token_service import EncodedToken, TokenService


class PyJwtTokenService(TokenService):
    def __init__(
        self,
        secret: str,
        algorithm: str,
        issuer: str,
        audience: str,
        access_expire_minutes: int,
        refresh_expire_days: int,
        leeway_seconds: int,
        clock: Clock,
    ) -> None:
        if algorithm not in {"HS256", "HS384", "HS512"}:
            raise ValueError("Unsupported JWT algorithm.")
        self._secret = secret
        self._algorithm = algorithm
        self._issuer = issuer
        self._audience = audience
        self._access_minutes = access_expire_minutes
        self._refresh_days = refresh_expire_days
        self._leeway = leeway_seconds
        self._clock = clock

    def create_access_token(
        self, subject: str, roles: list[str], token_version: int
    ) -> EncodedToken:
        now = self._clock.now()
        expires = now + timedelta(minutes=self._access_minutes)
        claims = self._base_claims(subject, "access", token_version, now, expires)
        claims["roles"] = list(roles)
        return self._encode(claims, now, expires)

    def create_refresh_token(
        self, subject: str, token_version: int, *, family: str | None = None
    ) -> EncodedToken:
        now = self._clock.now()
        expires = now + timedelta(days=self._refresh_days)
        claims = self._base_claims(subject, "refresh", token_version, now, expires)
        claims["family"] = family or str(uuid.uuid4())
        return self._encode(claims, now, expires)

    def decode(self, token: str, *, expected_type: str) -> dict[str, Any]:
        if expected_type not in {"access", "refresh"}:
            raise TokenError("Unsupported token type.")
        try:
            claims = jwt.decode(
                token,
                self._secret,
                algorithms=[self._algorithm],
                audience=self._audience,
                issuer=self._issuer,
                leeway=self._leeway,
                options={
                    "verify_exp": False,
                    "verify_nbf": False,
                    "verify_iat": False,
                    "require": [
                        "sub",
                        "type",
                        "jti",
                        "token_version",
                        "iat",
                        "nbf",
                        "exp",
                        "iss",
                        "aud",
                    ]
                },
            )
        except jwt.PyJWTError as exc:
            raise TokenError("Invalid or expired token.") from exc
        if claims.get("type") != expected_type:
            raise TokenError("Token type is invalid.")
        if expected_type == "refresh" and not claims.get("family"):
            raise TokenError("Refresh token family is missing.")
        if not isinstance(claims.get("sub"), str) or not isinstance(claims.get("token_version"), int):
            raise TokenError("Token claims are invalid.")
        now = self._epoch(self._clock.now())
        try:
            expires_at = int(claims["exp"])
            not_before = int(claims["nbf"])
            issued_at = int(claims["iat"])
        except (TypeError, ValueError) as exc:
            raise TokenError("Token time claims are invalid.") from exc
        if expires_at + self._leeway < now:
            raise TokenError("Invalid or expired token.")
        if not_before - self._leeway > now or issued_at - self._leeway > now:
            raise TokenError("Token is not active yet.")
        return claims

    def hash_token(self, token: str) -> str:
        return hmac.new(
            self._secret.encode("utf-8"), token.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    def verify_token_hash(self, token: str, token_hash: str) -> bool:
        return hmac.compare_digest(self.hash_token(token), token_hash)

    def _base_claims(
        self, subject: str, token_type: str, token_version: int, now, expires
    ) -> dict[str, Any]:
        return {
            "sub": subject,
            "type": token_type,
            "token_version": token_version,
            "iat": now,
            "nbf": now,
            "exp": expires,
            "jti": str(uuid.uuid4()),
            "iss": self._issuer,
            "aud": self._audience,
        }

    def _encode(self, claims: dict[str, Any], now, expires) -> EncodedToken:
        raw = jwt.encode(claims, self._secret, algorithm=self._algorithm)
        public_claims = dict(claims)
        for key in ("iat", "nbf", "exp"):
            public_claims[key] = self._epoch(claims[key])
        return EncodedToken(raw, public_claims, now, expires)

    @staticmethod
    def _epoch(value) -> int:
        """Interpret domain datetimes as naive UTC, independent of the host timezone."""
        aware = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
        return int(aware.timestamp())
