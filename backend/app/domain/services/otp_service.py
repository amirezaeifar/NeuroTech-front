from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import timedelta
from typing import Any

from app.core.exceptions import OtpAttemptsExceeded, OtpCooldownError, OtpError, OtpRateLimitError
from app.core.normalization import normalize_destination
from app.domain.entities.enums import OtpPurpose
from app.domain.ports.clock import Clock
from app.domain.ports.otp_sender import OtpSender
from app.domain.ports.otp_store import OtpRecord, OtpStore, OtpVerificationStatus
from app.domain.services.auth_service import AuthService, ClientContext


class OtpService:
    def __init__(
        self,
        store: OtpStore,
        sender: OtpSender,
        clock: Clock,
        auth_service: AuthService,
        *,
        hash_secret: str,
        expire_seconds: int,
        resend_cooldown_seconds: int,
        max_attempts: int,
        max_requests_per_hour: int,
        code_length: int,
        development_mode: bool,
    ) -> None:
        self._store = store
        self._sender = sender
        self._clock = clock
        self._auth = auth_service
        self._secret = hash_secret.encode("utf-8")
        self._expire_seconds = expire_seconds
        self._cooldown_seconds = resend_cooldown_seconds
        self._max_attempts = max_attempts
        self._max_requests = max_requests_per_hour
        self._length = code_length
        self._development_mode = development_mode

    def request_otp(self, destination: str, purpose: str) -> dict[str, Any]:
        normalized = normalize_destination(destination)
        parsed_purpose = OtpPurpose(purpose)
        code = "".join(secrets.choice("0123456789") for _ in range(self._length))
        now = self._clock.now()
        record = OtpRecord(
            purpose=parsed_purpose.value,
            destination=normalized,
            code_hash=self._hash(code),
            created_at=now,
            expires_at=now + timedelta(seconds=self._expire_seconds),
            attempt_count=0,
            max_attempts=self._max_attempts,
            request_count=1,
            resend_available_at=now + timedelta(seconds=self._cooldown_seconds),
        )
        self._store.create(
            record,
            ttl_seconds=self._expire_seconds,
            max_requests_per_hour=self._max_requests,
        )
        self._sender.send(normalized, code, parsed_purpose.value)
        result: dict[str, Any] = {"accepted": True}
        if self._development_mode:
            result["development_otp"] = code
        return result

    def verify_otp(
        self,
        destination: str,
        purpose: str,
        code: str,
        client: ClientContext | None = None,
    ) -> dict[str, Any]:
        normalized = normalize_destination(destination)
        parsed_purpose = OtpPurpose(purpose)
        status = self._store.verify_and_consume(
            parsed_purpose.value, normalized, self._hash(code)
        )
        if status is OtpVerificationStatus.ATTEMPTS_EXCEEDED:
            raise OtpAttemptsExceeded("Maximum OTP attempts exceeded.")
        if status is not OtpVerificationStatus.VERIFIED:
            raise OtpError("The verification code is invalid or expired.")
        if parsed_purpose is OtpPurpose.LOGIN:
            return self._auth.login_with_otp(normalized, client)
        return {"verified": True, "destination": normalized, "purpose": parsed_purpose.value}

    def consume_otp(self, destination: str, purpose: str) -> None:
        self._store.consume(OtpPurpose(purpose).value, normalize_destination(destination))

    def enforce_rate_limit(self) -> None:
        """Rate limiting is atomically enforced by the store during create."""

    def enforce_attempt_limit(self) -> None:
        """Attempt limiting is atomically enforced by the store during verification."""

    def enforce_resend_cooldown(self) -> None:
        """Cooldown is atomically enforced by the store during create."""

    def _hash(self, code: str) -> str:
        return hmac.new(self._secret, code.encode("utf-8"), hashlib.sha256).hexdigest()
