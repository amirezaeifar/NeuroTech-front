from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OtpVerificationStatus(str, Enum):
    VERIFIED = "verified"
    MISSING = "missing"
    INVALID = "invalid"
    ATTEMPTS_EXCEEDED = "attempts_exceeded"


@dataclass(frozen=True, slots=True)
class OtpRecord:
    purpose: str
    destination: str
    code_hash: str
    created_at: datetime
    expires_at: datetime
    attempt_count: int
    max_attempts: int
    request_count: int
    resend_available_at: datetime


class OtpStore(ABC):
    @abstractmethod
    def create(
        self,
        record: OtpRecord,
        *,
        ttl_seconds: int,
        max_requests_per_hour: int,
    ) -> None: ...

    @abstractmethod
    def verify_and_consume(
        self, purpose: str, destination: str, candidate_hash: str
    ) -> OtpVerificationStatus: ...

    @abstractmethod
    def consume(self, purpose: str, destination: str) -> None: ...
