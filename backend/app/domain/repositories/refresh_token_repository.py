from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities.refresh_token import RefreshToken


class RefreshTokenRepository(ABC):
    @abstractmethod
    def get_by_jti(self, jti: str) -> RefreshToken | None: ...

    @abstractmethod
    def add(self, token: RefreshToken) -> RefreshToken: ...

    @abstractmethod
    def revoke(
        self, token: RefreshToken, revoked_at: datetime, *, replaced_by_jti: str | None = None
    ) -> None: ...

    @abstractmethod
    def revoke_family(self, token_family: str, revoked_at: datetime) -> int: ...

    @abstractmethod
    def revoke_all_for_user(self, user_id: int, revoked_at: datetime) -> int: ...

    @abstractmethod
    def list_active_for_user(self, user_id: int, now: datetime) -> list[RefreshToken]: ...
