from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType

from app.domain.repositories.refresh_token_repository import RefreshTokenRepository
from app.domain.repositories.role_repository import RoleRepository
from app.domain.repositories.user_repository import UserRepository


class UnitOfWork(ABC):
    users: UserRepository
    roles: RoleRepository
    refresh_tokens: RefreshTokenRepository

    @abstractmethod
    def __enter__(self) -> "UnitOfWork": ...

    @abstractmethod
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...

    @abstractmethod
    def flush(self) -> None: ...
