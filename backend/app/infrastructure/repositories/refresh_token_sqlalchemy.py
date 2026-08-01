from __future__ import annotations

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.domain.entities.refresh_token import RefreshToken
from app.domain.repositories.refresh_token_repository import RefreshTokenRepository


class SqlAlchemyRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_jti(self, jti: str) -> RefreshToken | None:
        return self._session.scalar(select(RefreshToken).where(RefreshToken.jti == jti))

    def add(self, token: RefreshToken) -> RefreshToken:
        self._session.add(token)
        return token

    def revoke(
        self, token: RefreshToken, revoked_at: datetime, *, replaced_by_jti: str | None = None
    ) -> None:
        token.revoked_at = revoked_at
        token.replaced_by_jti = replaced_by_jti

    def revoke_family(self, token_family: str, revoked_at: datetime) -> int:
        result = self._session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.token_family == token_family,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=revoked_at)
        )
        return int(result.rowcount or 0)

    def revoke_all_for_user(self, user_id: int, revoked_at: datetime) -> int:
        result = self._session.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=revoked_at)
        )
        return int(result.rowcount or 0)

    def list_active_for_user(self, user_id: int, now: datetime) -> list[RefreshToken]:
        return list(
            self._session.scalars(
                select(RefreshToken).where(
                    RefreshToken.user_id == user_id,
                    RefreshToken.revoked_at.is_(None),
                    RefreshToken.expires_at > now,
                )
            )
        )
