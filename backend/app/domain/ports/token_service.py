from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class EncodedToken:
    raw: str
    claims: dict[str, Any]
    issued_at: datetime
    expires_at: datetime


class TokenService(ABC):
    @abstractmethod
    def create_access_token(
        self, subject: str, roles: list[str], token_version: int
    ) -> EncodedToken: ...

    @abstractmethod
    def create_refresh_token(
        self, subject: str, token_version: int, *, family: str | None = None
    ) -> EncodedToken: ...

    @abstractmethod
    def decode(self, token: str, *, expected_type: str) -> dict[str, Any]: ...

    @abstractmethod
    def hash_token(self, token: str) -> str: ...

    @abstractmethod
    def verify_token_hash(self, token: str, token_hash: str) -> bool: ...
